"""One startup snapshot of model/catalog; query embeddings belong to each client."""
from __future__ import annotations

import hashlib
import asyncio
import math
from dataclasses import dataclass
from pathlib import Path
from threading import BoundedSemaphore, Lock

import numpy as np

from search_engine.clip_model import embed_query, preload_model
from search_engine.database import Collection, load_collection
from search_engine.ranking import Result, rank
from search_engine.errors import SearchBusyError, SearchTimeoutError, visitor_error
from search_engine.validation import validate_description, validate_image_bytes
from search_engine.embeddings import validate_embeddings

MAX_ACTIVE_SEARCHES = 2
QUERY_TIMEOUT_SECONDS = 30
MAX_QUERY_RESULTS = 1000


@dataclass(frozen=True)
class QueryState:
    text: str
    image_digest: str | None
    text_vector: np.ndarray | None
    image_vector: np.ndarray | None


class SearchRuntime:
    def __init__(self, database: Path, *, max_active: int = MAX_ACTIVE_SEARCHES,
                 query_timeout: float = QUERY_TIMEOUT_SECONDS) -> None:
        if max_active < 1 or not math.isfinite(query_timeout) or query_timeout <= 0:
            raise ValueError('Search admission and timeout limits must be positive and finite.')
        self.database = database
        self.collection: Collection | None = None
        self.ready = False
        self.error = ''
        self._startup_lock = Lock()
        self._search_slots = BoundedSemaphore(max_active)
        self.query_timeout = query_timeout

    def initialize(self) -> None:
        with self._startup_lock:
            if self.ready:
                return
            try:
                self.collection = load_collection(self.database)
                for array in [*self.collection.vectors.values(), *self.collection.owners.values()]:
                    array.setflags(write=False)
                preload_model()
                self.ready = True
                self.error = ''
            except Exception as exc:
                self.error = visitor_error(exc, 'startup')
                raise

    async def submit_query(self, session: 'SearchSession', text: str, image: bytes | None) -> None:
        """Admit before queueing; retain the slot until cancelled/timed-out CPU work really ends."""
        validate_description(text)
        if image is not None:
            validate_image_bytes(image)
        if not self._search_slots.acquire(blocking=False):
            raise SearchBusyError

        def compute() -> QueryState:
            try:
                return session.prepare(text, image)
            finally:
                self._search_slots.release()

        worker = asyncio.create_task(asyncio.to_thread(compute))
        # A timed-out visitor no longer awaits this task; consume its eventual error.
        worker.add_done_callback(lambda task: None if task.cancelled() else task.exception())
        try:
            state = await asyncio.wait_for(asyncio.shield(worker), self.query_timeout)
        except TimeoutError as exc:
            raise SearchTimeoutError from exc
        # Only a successfully awaited request can publish per-client query state.
        session.commit(state)


class SearchSession:
    def __init__(self, runtime: SearchRuntime) -> None:
        self.runtime = runtime
        self.text = ''
        self.image_digest: str | None = None
        self.text_vector = None
        self.image_vector = None

    @property
    def has_query(self) -> bool:
        return self.text_vector is not None or self.image_vector is not None

    def submit(self, text: str, image: bytes | None) -> None:
        self.commit(self.prepare(text, image))

    def prepare(self, text: str, image: bytes | None) -> QueryState:
        if not self.runtime.ready:
            raise RuntimeError('Search is not available. Please try again later.')
        text = validate_description(text)
        if image is not None:
            validate_image_bytes(image)
        digest = hashlib.sha256(image).hexdigest() if image is not None else None
        # Stage updates so a failed input cannot leave a half-updated query.
        text_vector = self.text_vector
        image_vector = self.image_vector
        if text != self.text:
            text_vector = embed_query(text, None)[0] if text else None
        if digest != self.image_digest:
            if image is None:
                image_vector = None
            else:
                _, image_vector = embed_query('', image)
        if (text and text_vector is None) or (image is not None and image_vector is None):
            raise ValueError('The query encoder did not return the required embedding.')
        if text_vector is not None:
            text_vector = validate_embeddings(np.asarray([text_vector]), 1)[0]
        if image_vector is not None:
            image_vector = validate_embeddings(np.asarray([image_vector]), 1)[0]
        return QueryState(text, digest, text_vector, image_vector)

    def commit(self, state: QueryState) -> None:
        self.text, self.image_digest = state.text, state.image_digest
        self.text_vector, self.image_vector = state.text_vector, state.image_vector

    def results(self, classification: str = '') -> list[Result]:
        collection = self.runtime.collection
        if collection is None or not self.has_query:
            return []
        return rank(collection, query_text=self.text_vector, query_image=self.image_vector,
                    classification=classification, limit=MAX_QUERY_RESULTS)

    def reset(self) -> None:
        self.text = ''
        self.image_digest = None
        self.text_vector = self.image_vector = None
