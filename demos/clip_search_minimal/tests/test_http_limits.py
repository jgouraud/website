import asyncio

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from search_engine.http_limits import PublicCatalogImages, UploadLimitsMiddleware


def application(**limits):
    async def accept(request: Request):
        async with request.form() as form:
            file = next(iter(form.values()))
            return JSONResponse({'size': len(await file.read())})
    return UploadLimitsMiddleware(Starlette(routes=[Route('/upload/image', accept, methods=['POST'])]), **limits)


def test_real_multipart_boundary_accepts_one_file_and_rejects_extra_parts():
    async def scenario():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(application()), base_url='http://test') as client:
            response = await client.post('/upload/image', files={'file': ('part.png', b'abc', 'image/png')})
            assert response.status_code == 200 and response.json() == {'size': 3}
            response = await client.post('/upload/image', files=[('one', ('1.png', b'a')), ('two', ('2.png', b'b'))])
            assert response.status_code == 400
            response = await client.post('/upload/image', files={'file': ('part.png', b'a')}, data={'extra': 'field'})
            assert response.status_code == 400
    asyncio.run(scenario())


def test_chunked_upload_is_limited_even_without_content_length():
    async def scenario():
        async def chunks():
            yield b'a' * 8
            yield b'b' * 8
            raise AssertionError('Oversized receipt must stop before requesting more bytes')
        async with httpx.AsyncClient(transport=httpx.ASGITransport(application(max_body_bytes=10)), base_url='http://test') as client:
            response = await client.post('/upload/image', content=chunks(), headers={'Content-Type': 'multipart/form-data; boundary=test'})
            assert response.status_code == 413
    asyncio.run(scenario())


def test_slow_upload_has_a_finite_receipt_deadline():
    async def scenario():
        blocked = asyncio.Event()
        async def chunks():
            await blocked.wait()
            yield b'never delivered'
        async with httpx.AsyncClient(transport=httpx.ASGITransport(application(receipt_seconds=.02)), base_url='http://test') as client:
            response = await client.post('/upload/image', content=chunks(), headers={'Content-Type': 'multipart/form-data; boundary=test'})
            assert response.status_code == 408
    asyncio.run(scenario())


def test_upload_admission_rejects_overload_and_releases_cancelled_receipt():
    async def scenario():
        entered, release = asyncio.Event(), asyncio.Event()
        async def chunks():
            entered.set()
            await release.wait()
            yield b'x'
        app = application(max_concurrent=1)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://test') as client:
            pending = asyncio.create_task(client.post('/upload/image', content=chunks(), headers={'Content-Type': 'multipart/form-data; boundary=test'}))
            await asyncio.wait_for(entered.wait(), 1)
            response = await client.post('/upload/image', files={'file': ('part.png', b'a')})
            assert response.status_code == 429
            pending.cancel()
            try:
                await pending
            except asyncio.CancelledError:
                pass
            response = await client.post('/upload/image', files={'file': ('part.png', b'a')})
            assert response.status_code == 200
    asyncio.run(scenario())


def test_staged_images_and_provenance_are_never_public(tmp_path):
    stage = tmp_path / '.catalog-stage-private'
    stage.mkdir()
    (stage / 'part.png').write_bytes(b'not ready')
    generation = tmp_path / 'catalog-complete'
    generation.mkdir()
    (generation / 'part.png').write_bytes(b'complete image')
    (generation / 'manifest.json').write_text('{"source_path":"private"}')

    async def scenario():
        app = Starlette(routes=[Mount('/', app=PublicCatalogImages(directory=str(tmp_path)))])
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://test') as client:
            for path in ('/.catalog-stage-private/part.png', '/catalog-complete/manifest.json'):
                response = await client.get(path)
                assert response.status_code == 404
            response = await client.get('/catalog-complete/part.png')
            assert response.status_code == 200 and response.content == b'complete image'
            assert response.headers['x-content-type-options'] == 'nosniff'
    asyncio.run(scenario())
