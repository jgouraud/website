from contextlib import contextmanager, closing
from pathlib import Path
import os
import socket
import sqlite3
import subprocess
import sys
from threading import Event, Thread

import pytest

ROOT = Path(__file__).resolve().parents[2]


@contextmanager
def _serve(tmp_path_factory, command_for_port, extra_environment=None):
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    log_path = tmp_path_factory.mktemp('web-server') / 'server.log'
    environment = {key: value for key, value in os.environ.items() if key != 'PYTEST_CURRENT_TEST'}
    environment.update(extra_environment or {})
    process = subprocess.Popen(command_for_port(port), cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding='utf-8', env={**environment, 'PYTHONUTF8': '1'},
                               creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
    ready = Event()
    started = Event()

    def capture():
        with log_path.open('w', encoding='utf-8') as output:
            for line in process.stdout:
                output.write(line)
                output.flush()
                if 'NiceGUI ready to go' in line:
                    started.set()
                    ready.set()
        ready.set()  # Surface a failed startup immediately instead of waiting 30 seconds.

    reader = Thread(target=capture, daemon=True)
    reader.start()
    try:
        if not ready.wait(timeout=30) or not started.is_set():
            pytest.fail(f'App did not become ready. Log: {log_path.read_text(encoding="utf-8")}')
        yield f'http://127.0.0.1:{port}'
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        reader.join(timeout=2)
        process.stdout.close()


@pytest.fixture(scope='session')
def homepage_url(tmp_path_factory):
    with _serve(tmp_path_factory, lambda port: [
        sys.executable, str(ROOT / 'tests/browser/serve_partfinder.py'), str(port),
    ]) as url:
        yield url


@pytest.fixture(scope='session')
def partfinder_url(tmp_path_factory):
    import numpy as np
    from PIL import Image

    directory = tmp_path_factory.mktemp('synthetic-catalog')
    images = directory / 'images'
    images.mkdir()
    database = directory / 'catalog.db'
    with closing(sqlite3.connect(database)) as connection:
        connection.executescript('''
            CREATE TABLE catalog_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE items (
                id TEXT NOT NULL, name TEXT NOT NULL, classification TEXT NOT NULL,
                image_path TEXT NOT NULL, image_raw BLOB, image_embedding BLOB NOT NULL,
                source_path TEXT NOT NULL, source_split TEXT NOT NULL,
                vertex_count INTEGER, triangle_count INTEGER,
                PRIMARY KEY (source_split, classification, id)
            );
        ''')
        connection.execute('INSERT INTO catalog_metadata VALUES (?, ?)', ('embedding_model', 'ViT-B/32'))
        for index, name in enumerate(('Test gear', 'Test washer')):
            image_path = f'{index}.png'
            Image.new('RGB', (32, 32), ('gray', 'white')[index]).save(images / image_path)
            vector = np.eye(2, 512, dtype=np.float32)[index]
            connection.execute('''INSERT INTO items
                (id,name,classification,image_path,image_raw,image_embedding,
                 source_path,source_split,vertex_count,triangle_count) VALUES (?,?,?,?,?,?,?,?,?,?)''',
                (str(index), name, name.split()[-1], image_path, (images / image_path).read_bytes(),
                 vector.tobytes(), 'synthetic.obj', 'test', 3, 1))
        connection.commit()
    with _serve(tmp_path_factory, lambda port: [
        sys.executable, str(ROOT / 'tests/browser/serve_partfinder.py'), str(port),
    ], {'CLIP_SEARCH_DB': str(database), 'CLIP_SEARCH_IMAGES': str(images)}) as url:
        yield url + '/partfinder?lang=EN'


@pytest.fixture(scope='session')
def browser():
    from playwright.sync_api import sync_playwright

    options = {'headless': True}
    executable = os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE')
    if executable:
        options['executable_path'] = executable
    elif sys.platform == 'win32' and Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe').is_file():
        options['executable_path'] = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={'width': 1366, 'height': 768})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    yield page
    context.close()
    assert not errors, errors
