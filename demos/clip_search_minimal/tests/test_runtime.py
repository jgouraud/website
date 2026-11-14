from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pytest

from search_engine.database import Collection
from search_engine import runtime as module


def collection():
    vectors = np.eye(2, 512, dtype=np.float32)
    return Collection(['001', '002'], ['Gear', 'Washer'], ['', ''],
                      {'image': vectors}, {'image': np.arange(2, dtype=np.int32)},
                      ['gear', 'washer'])


def prepared_runtime(monkeypatch):
    calls = []
    monkeypatch.setattr(module, 'load_collection', lambda path: calls.append('catalog') or collection())
    monkeypatch.setattr(module, 'preload_model', lambda: calls.append('model'))
    engine = module.SearchRuntime(Path('catalog.db'))
    engine.initialize()
    return engine, calls


def test_startup_is_once_even_with_concurrent_callers(monkeypatch):
    engine, calls = prepared_runtime(monkeypatch)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: engine.initialize(), range(8)))
    assert calls == ['catalog', 'model']
    assert engine.ready
    with pytest.raises(ValueError):
        engine.collection.vectors['image'][0, 0] = 42


def test_query_changes_encode_only_changed_inputs_and_filters_encode_nothing(monkeypatch):
    engine, startup_calls = prepared_runtime(monkeypatch)
    encoded = []
    vector = np.eye(1, 512, dtype=np.float32)[0]

    def embed(text, image):
        encoded.append((text, image))
        return (vector if text else None, vector if image else None)

    monkeypatch.setattr(module, 'embed_query', embed)
    session = module.SearchSession(engine)
    session.submit(' gear ', b'image-one')
    session.submit('gear', bytes(b'image-one'))
    assert encoded == [('gear', None), ('', b'image-one')]
    for category, expected in [('washer', '002'), ('gear', '001')]:
        results = session.results(classification=category)
        assert [result.item_id for result in results] == [expected]
        assert all(set(result.scores) == {'global', 'image', 'text_to_image'} for result in results)
    assert len(encoded) == 2 and startup_calls == ['catalog', 'model']
    session.submit('washer', b'image-one')
    assert encoded[-1] == ('washer', None) and len(encoded) == 3
    session.submit('washer', b'image-two')
    assert encoded[-1] == ('', b'image-two') and len(encoded) == 4
    session.submit('', None)
    assert not session.has_query and session.results() == [] and len(encoded) == 4


def test_client_query_state_is_isolated_and_failed_input_keeps_previous_query(monkeypatch):
    engine, _ = prepared_runtime(monkeypatch)
    vector = np.eye(1, 512, dtype=np.float32)[0]

    def embed(text, image):
        if image:
            raise ValueError('bad image')
        return vector, None

    monkeypatch.setattr(module, 'embed_query', embed)
    first, second = module.SearchSession(engine), module.SearchSession(engine)
    first.submit('gear', None)
    assert first.has_query and not second.has_query
    with pytest.raises(ValueError, match='bad image'):
        first.submit('new description', b'broken')
    assert first.text == 'gear' and first.image_digest is None
    first.reset()
    assert not first.has_query and first.results() == []


def test_model_failure_keeps_catalog_cached_but_blocks_inference(monkeypatch):
    monkeypatch.setattr(module, 'load_collection', lambda path: collection())

    def fail():
        raise RuntimeError('missing checkpoint')

    monkeypatch.setattr(module, 'preload_model', fail)
    engine = module.SearchRuntime(Path('catalog.db'))
    with pytest.raises(RuntimeError, match='missing checkpoint'):
        engine.initialize()
    assert not engine.ready and 'missing checkpoint' not in engine.error
    assert 'Reference:' in engine.error
    session = module.SearchSession(engine)
    assert engine.collection.size == 2 and session.results() == []
    with pytest.raises(RuntimeError, match='not available'):
        session.submit('gear', None)


def test_mesh_search_combined_score_ignores_legacy_geometry(monkeypatch):
    engine, _ = prepared_runtime(monkeypatch)
    vector = np.eye(1, 512, dtype=np.float32)[0]
    monkeypatch.setattr(module, 'embed_query', lambda text, image: (None, vector))
    session = module.SearchSession(engine)
    session.submit('', b'rendering')
    baseline = [(result.item_id, result.scores['global']) for result in session.results()]
    engine.collection.vectors['geometry'] = engine.collection.vectors['image'][::-1].copy()
    assert [(result.item_id, result.scores['global']) for result in session.results()] == baseline
    assert all('geometry' not in result.scores for result in session.results())
    assert session.results()[0].scores['global'] == 1.0


@pytest.mark.parametrize('bad', ['nan', 'zero', 'shape'])
def test_invalid_model_output_cannot_replace_previous_query(monkeypatch, bad):
    engine, _ = prepared_runtime(monkeypatch)
    vector = np.eye(1, 512, dtype=np.float32)[0]
    monkeypatch.setattr(module, 'embed_query', lambda text, image: (vector, None))
    session = module.SearchSession(engine)
    session.submit('gear', None)
    invalid = np.full(512, np.nan, dtype=np.float32) if bad == 'nan' else np.zeros(512 if bad == 'zero' else 12, dtype=np.float32)
    monkeypatch.setattr(module, 'embed_query', lambda text, image: (invalid, None))
    with pytest.raises(ValueError, match='Invalid CLIP embedding'):
        session.submit('washer', None)
    assert session.text == 'gear'
    np.testing.assert_array_equal(session.text_vector, vector)
