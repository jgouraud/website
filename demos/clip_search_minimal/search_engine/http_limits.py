"""Bound upload receipt before NiceGUI's multipart parsing or image decoding."""
import asyncio
from threading import BoundedSemaphore
from pathlib import PurePosixPath

from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.formparsers import MultiPartException
from starlette.responses import PlainTextResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.staticfiles import StaticFiles

from search_engine.validation import MAX_IMAGE_BYTES

MAX_UPLOAD_BODY_BYTES = MAX_IMAGE_BYTES + 64 * 1024
UPLOAD_RECEIPT_SECONDS = 30
MAX_CONCURRENT_UPLOADS = 2


class PublicCatalogImages(StaticFiles):
    """Serve completed images, never staging directories or build manifests."""
    async def get_response(self, path: str, scope: Scope) -> Response:
        relative = PurePosixPath(path)
        if any(part.startswith('.') for part in relative.parts) or relative.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.gif'}:
            raise HTTPException(status_code=404)
        response = await super().get_response(path, scope)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response


class UploadLimitsMiddleware:
    def __init__(self, app: ASGIApp, *, max_body_bytes: int = MAX_UPLOAD_BODY_BYTES,
                 receipt_seconds: float = UPLOAD_RECEIPT_SECONDS,
                 max_concurrent: int = MAX_CONCURRENT_UPLOADS) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes
        self.receipt_seconds = receipt_seconds
        self.slots = BoundedSemaphore(max_concurrent)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] != 'http' or '/upload/' not in scope.get('path', ''):
            await self.app(scope, receive, send)
            return
        if not self.slots.acquire(blocking=False):
            await PlainTextResponse('Uploads are busy. Try again shortly.', 429)(scope, receive, send)
            return
        try:
            types = [value for name, value in scope['headers'] if name.lower() == b'content-type']
            if len(types) != 1 or types[0].split(b';', 1)[0].strip().lower() != b'multipart/form-data':
                await PlainTextResponse('Use a multipart image upload.', 415)(scope, receive, send)
                return
            lengths = [value for name, value in scope['headers'] if name.lower() == b'content-length']
            try:
                length = int(lengths[0]) if lengths else 0
                if len(lengths) > 1 or length < 0:
                    raise ValueError
            except ValueError:
                await PlainTextResponse('Invalid upload length.', 400)(scope, receive, send)
                return
            if length > self.max_body_bytes:
                await PlainTextResponse('Choose an image smaller than 12 MB.', 413)(scope, receive, send)
                return
            buffer = bytearray()
            total = 0
            try:
                async with asyncio.timeout(self.receipt_seconds):
                    while True:
                        message = await receive()
                        if message['type'] == 'http.disconnect':
                            return
                        total += len(message.get('body', b''))
                        if total > self.max_body_bytes:
                            await PlainTextResponse('Choose an image smaller than 12 MB.', 413)(scope, receive, send)
                            return
                        buffer.extend(message.get('body', b''))
                        if not message.get('more_body', False):
                            break
            except TimeoutError:
                await PlainTextResponse('Upload timed out. Try again.', 408)(scope, receive, send)
                return
            body = bytes(buffer)
            del buffer

            def replay() -> Receive:
                sent = False

                async def read() -> Message:
                    nonlocal sent
                    if not sent:
                        sent = True
                        return {'type': 'http.request', 'body': body, 'more_body': False}
                    return await receive()
                return read

            # The same maintained parser used by NiceGUI checks cardinality first.
            # Both passes consume the identical bounded bytes; no custom multipart grammar.
            request = Request(scope, replay())
            try:
                async with request.form(max_files=1, max_fields=0) as form:
                    if len(form) != 1 or not hasattr(next(iter(form.values())), 'size'):
                        raise ValueError('Expected exactly one image.')
                    size = next(iter(form.values())).size
                    if size is None or size > MAX_IMAGE_BYTES:
                        await PlainTextResponse('Choose an image smaller than 12 MB.', 413)(scope, receive, send)
                        return
            except (ValueError, OSError, HTTPException, MultiPartException):
                await PlainTextResponse('Upload exactly one image.', 400)(scope, receive, send)
                return
            await self.app(scope, replay(), send)
        finally:
            self.slots.release()
