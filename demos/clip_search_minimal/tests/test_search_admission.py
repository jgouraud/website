import asyncio
from threading import Event

import numpy as np
import pytest

from search_engine import runtime as runtime_module
from search_engine.runtime import SearchRuntime, SearchSession
from search_engine.errors import SearchBusyError, SearchTimeoutError


@pytest.mark.parametrize('end_request', ['timeout', 'cancel'])
def test_abandoned_search_keeps_its_slot_and_cannot_commit_query_state(tmp_path, monkeypatch, end_request):
    entered, release = Event(), Event()

    def encode(text, image):
        entered.set()
        if not release.wait(timeout=5):
            raise RuntimeError('Test did not release its controlled model worker.')
        return np.eye(1, 512, dtype=np.float32)[0], None

    monkeypatch.setattr(runtime_module, 'embed_query', encode)
    runtime = SearchRuntime(tmp_path / 'unused.db', max_active=1,
                            query_timeout=.1 if end_request == 'timeout' else 5)
    runtime.ready = True
    session = SearchSession(runtime)

    async def scenario():
        existing_tasks = asyncio.all_tasks()
        request = asyncio.create_task(runtime.submit_query(session, 'gear', None))
        try:
            assert await asyncio.to_thread(entered.wait, 2)
            if end_request == 'cancel':
                request.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await request
            else:
                with pytest.raises(SearchTimeoutError):
                    await request
            with pytest.raises(SearchBusyError):
                await runtime.submit_query(SearchSession(runtime), 'washer', None)
            assert not session.has_query and session.text == ''
        finally:
            release.set()
            # Await owned background work, without a timing sleep or leaking a worker.
            pending = asyncio.all_tasks() - existing_tasks
            await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), 3)
        assert not session.has_query and session.text == ''
        await runtime.submit_query(session, 'washer', None)
        assert session.has_query and session.text == 'washer'

    asyncio.run(scenario())
