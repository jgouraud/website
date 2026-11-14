import sqlite3

import numpy as np
import pytest

from search_engine.database import load_collection
from search_engine.images import preview_url
from search_engine.ranking import rank


def vector(index: int) -> np.ndarray:
    result = np.zeros(512, dtype=np.float32)
    result[index] = 1
    return result


def make_db(tmp_path):
    db = tmp_path / 'catalog.db'
    with sqlite3.connect(db) as conn:
        conn.executescript('''
        CREATE TABLE Images (Trial INTEGER PRIMARY KEY, file_path TEXT, embedded_text BLOB);
        CREATE TABLE ImageViews (id INTEGER PRIMARY KEY, image_id INTEGER, file_path TEXT, image_embedding BLOB);
        CREATE TABLE CropsDescription (id INTEGER PRIMARY KEY, image_id INTEGER, text_embedding BLOB);
        CREATE TABLE BlackAndWhiteCrops (id INTEGER PRIMARY KEY, image_id INTEGER, image_embedding BLOB);
        ''')
        conn.executemany('INSERT INTO Images VALUES (?, ?, ?)', [(1, 'images/a.png', None), (2, 'images/b.png', None)])
        conn.executemany('INSERT INTO ImageViews (image_id, file_path, image_embedding) VALUES (?, ?, ?)', [
            (1, 'images/a.png', vector(0).tobytes()),
            (2, 'images/b.png', vector(1).tobytes()),
        ])
        conn.executemany('INSERT INTO CropsDescription (image_id, text_embedding) VALUES (?, ?)', [
            (1, vector(0).tobytes()), (2, vector(1).tobytes()),
        ])
    return db


def test_load_and_rank_read_only(tmp_path):
    db = make_db(tmp_path)
    before = db.read_bytes()
    collection = load_collection(db)
    assert collection.size == 2
    assert len(collection.vectors['image']) == 2
    assert rank(collection, query_text=vector(0))[0].item_id == '1'
    assert rank(collection, query_image=vector(1))[0].item_id == '2'
    assert rank(collection, query_text=vector(0), query_image=vector(0))[0].item_id == '1'
    assert db.read_bytes() == before


def test_legacy_text_embeddings_alone_cannot_produce_matches(tmp_path):
    db = tmp_path / 'minimal.db'
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE Images (Trial INTEGER PRIMARY KEY, file_path TEXT, embedded_text BLOB)')
        conn.execute('INSERT INTO Images VALUES (?, ?, ?)', (3, 'thing.png', vector(2).tobytes()))
    collection = load_collection(db)
    assert 'text' not in collection.vectors
    assert rank(collection, query_text=vector(2)) == []
    assert rank(collection, query_image=vector(2)) == []


def test_empty_and_missing_db(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_collection(tmp_path / 'unknown.db')
    db = make_db(tmp_path)
    collection = load_collection(db)
    with pytest.raises(ValueError):
        rank(collection)


def test_image_paths_stay_within_public_root(tmp_path, monkeypatch):
    from search_engine import images
    root = tmp_path / 'images'
    root.mkdir()
    (root / 'example.png').write_bytes(b'not-an-image')
    (tmp_path / 'secret.png').write_bytes(b'private')
    monkeypatch.setattr(images, 'IMAGE_ROOT', root)
    assert preview_url('output_data/images/example.png') == '/catalog-images/example.png'
    assert preview_url('../secret.png') is None
    assert preview_url(str(tmp_path / 'secret.png')) is None


def test_legacy_grayscale_embeddings_are_ignored(tmp_path):
    db = make_db(tmp_path)
    with sqlite3.connect(db) as conn:
        conn.executemany('INSERT INTO BlackAndWhiteCrops (image_id, image_embedding) VALUES (?, ?)', [
            (1, vector(1).tobytes()), (2, vector(0).tobytes()),
        ])
    collection = load_collection(db)
    results = rank(collection, query_image=vector(0))
    assert results[0].item_id == '1'
    assert set(collection.vectors) == {'image'}
    assert set(results[0].scores) == {'global', 'image', 'text_to_image'}


def make_sample_catalog(tmp_path):
    from search_engine.settings import MODEL_NAME

    db = tmp_path / 'samples.db'
    with sqlite3.connect(db) as connection:
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
        connection.execute('INSERT INTO catalog_metadata VALUES (?, ?)', ('embedding_model', MODEL_NAME))
        for item_id, category, index in [('0001', 'gear', 0), ('0002', 'washer', 1)]:
            connection.execute('''INSERT INTO items
                (id, name, classification, image_path, image_raw,
                 image_embedding, source_path, source_split,
                 vertex_count, triangle_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (item_id, category.title(), category,
                 f'{item_id}.png', b'raw-preview-bytes', vector(index).tobytes(),
                 f'MCB_B/train/{category}/{item_id}.obj', 'train', 3, 1))
    return db


def test_sample_catalog_round_trip_and_read_only(tmp_path):
    db = make_sample_catalog(tmp_path)
    before = db.read_bytes()
    collection = load_collection(db)
    assert collection.ids == ['0001', '0002']
    assert collection.classifications == ['gear', 'washer']
    assert 'text' not in collection.vectors
    assert collection.vectors['image'].shape == (2, 512)
    with sqlite3.connect(db) as connection:
        assert connection.execute('SELECT image_raw FROM items WHERE id = ?', ('0001',)).fetchone()[0] == b'raw-preview-bytes'
    assert db.read_bytes() == before


def test_classification_filters_browsing_and_all_search_channels(tmp_path):
    from search_engine.ranking import browse

    collection = load_collection(make_sample_catalog(tmp_path))
    assert [result.item_id for result in browse(collection, classification='washer')] == ['0002']
    assert browse(collection, classification='unknown') == []
    for channel in ['global', 'image', 'text_to_image']:
        results = rank(collection, query_text=vector(0), query_image=vector(0),
                       classification='washer', sort_by=channel)
        assert [result.item_id for result in results] == ['0002']
        assert results[0].classification == 'washer'
        assert results[0].scores[channel] == 1.0
    assert rank(collection, query_text=vector(0), classification='unknown') == []


@pytest.mark.parametrize('query', ['text', 'image', 'both'])
@pytest.mark.parametrize('catalog', ['sample', 'legacy'])
def test_ranking_uses_only_catalog_images(tmp_path, query, catalog):
    db = make_sample_catalog(tmp_path) if catalog == 'sample' else make_db(tmp_path)
    collection = load_collection(db)
    assert 'text' not in collection.vectors
    # Contradictory legacy text vectors must not influence either query mode.
    collection.vectors['text'] = np.stack([vector(1), vector(0)])
    collection.owners['text'] = np.arange(2, dtype=np.int32)
    kwargs = dict(query_text=vector(0) if query != 'image' else None,
                  query_image=vector(0) if query != 'text' else None)
    results = rank(collection, **kwargs)
    expected_id = '0001' if catalog == 'sample' else '1'
    assert results[0].item_id == expected_id
    assert results[0].scores['global'] == 1.0
    assert all(set(result.scores) == {'global', 'image', 'text_to_image'} for result in results)
    del collection.vectors['text'], collection.owners['text']
    without_text = rank(collection, **kwargs)
    assert [result.item_id for result in without_text] == [result.item_id for result in results]
    np.testing.assert_allclose([list(result.scores.values()) for result in without_text],
                               [list(result.scores.values()) for result in results], equal_nan=True)


def test_v1_catalog_extra_columns_are_ignored(tmp_path):
    db = make_sample_catalog(tmp_path)
    with sqlite3.connect(db) as connection:
        connection.execute('ALTER TABLE items ADD COLUMN full_text TEXT')
        connection.execute('ALTER TABLE items ADD COLUMN text_source TEXT')
        connection.execute('ALTER TABLE items ADD COLUMN text_embedding BLOB')
        connection.execute('ALTER TABLE items ADD COLUMN geometry_embedding BLOB')
        connection.execute("INSERT INTO catalog_metadata VALUES ('schema_version', '1')")
        connection.execute('UPDATE items SET full_text = ?, text_embedding = ?, geometry_embedding = ?',
                           ('unused description', vector(1).tobytes(), vector(1).tobytes()))
    before = db.read_bytes()
    collection = load_collection(db)
    assert set(collection.vectors) == {'image'}
    assert rank(collection, query_text=vector(0))[0].item_id == '0001'
    assert db.read_bytes() == before


def test_catalog_model_mismatch_is_rejected(tmp_path):
    db = make_sample_catalog(tmp_path)
    with sqlite3.connect(db) as connection:
        connection.execute("UPDATE catalog_metadata SET value = 'different-model' WHERE key = 'embedding_model'")
    with pytest.raises(ValueError, match='same CLIP model'):
        load_collection(db)


def test_large_finite_catalog_vector_is_normalized_without_overflow(tmp_path):
    db = make_db(tmp_path)
    with sqlite3.connect(db) as connection:
        connection.execute('UPDATE ImageViews SET image_embedding = ?',
                           (np.full(512, np.finfo(np.float32).max, dtype=np.float32).tobytes(),))
    collection = load_collection(db)
    assert np.isfinite(collection.vectors['image']).all()
    np.testing.assert_allclose(np.linalg.norm(collection.vectors['image'], axis=1), 1, atol=1e-6)


@pytest.mark.parametrize('bad_value', [np.nan, np.inf, -np.inf])
def test_nonfinite_query_vectors_are_rejected(tmp_path, bad_value):
    collection = load_collection(make_db(tmp_path))
    query = vector(0)
    query[1] = bad_value
    with pytest.raises(ValueError, match='finite'):
        rank(collection, query_image=query)
