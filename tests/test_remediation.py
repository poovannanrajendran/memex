import hashlib
import json
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from scripts import ingest, watcher, delivery
from scripts.db import Database
from scripts.lock import pipeline_lock, LockAcquisitionError


def fake_database(cursor):
    db = object.__new__(Database)
    @contextmanager
    def get_cursor():
        yield cursor
    db.get_cursor = get_cursor
    return db


def test_registration_database_error_is_not_skip(tmp_path):
    path = tmp_path / 'source.md'
    path.write_text('content')
    cursor = MagicMock()
    cursor.execute.side_effect = RuntimeError('database down')
    with pytest.raises(RuntimeError, match='Cannot register'):
        fake_database(cursor).register_file('run', str(path), 'article')


def test_missing_hash_does_not_skip_same_size(tmp_path):
    path = tmp_path / 'source.md'
    path.write_text('AAAA')
    cursor = MagicMock()
    cursor.fetchone.side_effect = [dict(status='completed', content_hash=None, file_size_bytes=4), dict(id=4)]
    assert fake_database(cursor).register_file('run', str(path), 'article') == 4


def test_missing_source_fails_before_database():
    with pytest.raises(FileNotFoundError):
        fake_database(MagicMock()).register_file('run', 'missing.md', 'article')


def test_standalone_tracks_file_and_finalises_under_lock(tmp_path, monkeypatch):
    db = MagicMock()
    db.register_file.return_value = 42
    monkeypatch.setattr(ingest, 'db', db)
    monkeypatch.setattr('scripts.lock.LOCK_FILE', str(tmp_path / 'pipeline.lock'))
    order = []
    def assert_locked(label):
        with pytest.raises(LockAcquisitionError):
            with pipeline_lock():
                pass
        order.append(label)
    monkeypatch.setattr(ingest, 'ingest_file', lambda *args: assert_locked('ingest'))
    monkeypatch.setattr(ingest, 'finalise_source', lambda *args: assert_locked('finalise'))
    with pipeline_lock():
        ingest.run_standalone('raw/articles/a.md', MagicMock(), 'model', 'api-run')
    assert order == ['ingest', 'finalise']
    db.register_file.assert_called_once_with('api-run', 'raw/articles/a.md', 'article')
    db.complete_run.assert_called_once_with('api-run', 'completed', 1, 1, 0, 0)


def test_standalone_skip_uses_no_model_but_finalises(monkeypatch):
    db = MagicMock()
    db.register_file.return_value = None
    monkeypatch.setattr(ingest, 'db', db)
    model_call = MagicMock()
    finalise = MagicMock()
    monkeypatch.setattr(ingest, 'ingest_file', model_call)
    monkeypatch.setattr(ingest, 'finalise_source', finalise)
    ingest.run_standalone('raw/a.md', MagicMock(), 'model', 'api-run')
    model_call.assert_not_called()
    finalise.assert_called_once()
    db.complete_run.assert_called_once_with('api-run', 'completed', 1, 0, 1, 0)


def test_standalone_failure_marks_run_and_file_failed(monkeypatch):
    db = MagicMock()
    db.register_file.return_value = 42
    monkeypatch.setattr(ingest, 'db', db)
    monkeypatch.setattr(ingest, 'ingest_file', MagicMock(side_effect=RuntimeError('model failed')))
    with pytest.raises(RuntimeError, match='model failed'):
        ingest.run_standalone('raw/a.md', MagicMock(), 'model', 'api-run')
    assert db.complete_run.call_args.args[1] == 'failed'
    assert db.update_file.call_args.args == (42, 'failed')


def test_finalisation_error_is_not_completed(monkeypatch):
    db = MagicMock()
    db.register_file.return_value = 42
    monkeypatch.setattr(ingest, 'db', db)
    monkeypatch.setattr(ingest, 'ingest_file', MagicMock())
    monkeypatch.setattr(ingest, 'finalise_source', MagicMock(side_effect=RuntimeError('push failed')))
    with pytest.raises(RuntimeError, match='push failed'):
        ingest.run_standalone('raw/a.md', MagicMock(), 'model', 'api-run')
    assert db.complete_run.call_args.args[:6] == ('api-run', 'failed', 1, 1, 0, 1)


def test_lock_does_not_relabel_io_error(tmp_path, monkeypatch):
    monkeypatch.setattr('scripts.lock.LOCK_FILE', str(tmp_path / 'pipeline.lock'))
    with pytest.raises(OSError, match='disk failure'):
        with pipeline_lock():
            raise OSError('disk failure')


def test_exact_database_slug_used_for_unicode_source(tmp_path):
    (tmp_path / 'wiki/sources').mkdir(parents=True)
    (tmp_path / 'wiki/sources/actual.md').write_text('Generated source')
    (tmp_path / 'wiki_index.json').write_text(json.dumps({'sources': {'actual': {'title': 'Actual'}}}))
    cursor = MagicMock()
    cursor.fetchone.return_value = {'wiki_slug': 'actual'}
    delivery.enqueue_source(fake_database(cursor), 'run', 'raw/தமிழ்.md')
    params = cursor.execute.call_args.args[1]
    assert params[1] == 'sources:actual'
    assert json.loads(params[3])['slug'] == 'actual'


def test_missing_slug_is_visible_error():
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match='No recorded wiki_slug'):
        delivery.enqueue_source(fake_database(cursor), 'run', 'raw/a.md')


@pytest.mark.parametrize('vector', [[0] * 768, [1] * 4, [float('nan')] * 768])
def test_invalid_embedding_is_rejected(vector):
    with pytest.raises(ValueError):
        delivery.validate_vector(vector)


def test_real_embedding_and_confirmed_qdrant_write(monkeypatch):
    monkeypatch.setenv('MEMEX_EMBED_URL', 'http://embed.test')
    monkeypatch.setenv('MEMEX_EMBED_TOKEN', 'test-token')
    session = MagicMock()
    session.post.return_value.json.return_value = {'model': 'nomic-embed-text:latest', 'embeddings': [[0.1] * 768]}
    session.get.return_value.json.return_value = {'result': {'config': {'params': {'vectors': {'size': 768}}}}}
    session.put.return_value.json.return_value = {'status': 'ok', 'result': {'status': 'completed'}}
    payload = {'type': 'sources', 'slug': 'a', 'title': 'A', 'text': 'some content'}
    first = delivery.deliver(payload, session)
    second = delivery.deliver(payload, session)
    assert first == second
    assert session.post.call_args.kwargs['json']['input'].startswith('search_document: ')
    assert session.put.call_args.args[0].endswith('?wait=true')
    assert any(session.put.call_args.kwargs['json']['points'][0]['vector'])


def test_http_failure_is_not_success(monkeypatch):
    monkeypatch.setenv('MEMEX_EMBED_URL', 'http://embed.test')
    monkeypatch.setenv('MEMEX_EMBED_TOKEN', 'token')
    session = MagicMock()
    session.post.return_value.raise_for_status.side_effect = RuntimeError('HTTP 503')
    with pytest.raises(RuntimeError, match='503'):
        delivery.deliver({'title': 'a', 'text': 'b'}, session)
    session.put.assert_not_called()


def test_outbox_failure_stays_pending_with_retry():
    cursor = MagicMock()
    cursor.fetchall.return_value = [{'id': 1, 'payload': {}, 'attempts': 0}]
    cursor.fetchone.return_value = {'pending': 1}
    sender = MagicMock(side_effect=RuntimeError('offline'))
    result = delivery.drain_outbox(fake_database(cursor), sender=sender)
    assert result == {'delivered': 0, 'failed': 1, 'pending': 1}
    updates = [c.args[0] for c in cursor.execute.call_args_list if 'UPDATE' in c.args[0]]
    assert len(updates) == 1 and 'next_attempt_at' in updates[0]
    assert "status='delivered'" not in updates[0]


def test_non_latin_slug_never_empty_or_shared():
    assert ingest.slugify('தமிழ்')
    assert ingest.slugify('தமிழ்') != ingest.slugify('வணக்கம்')


def test_watcher_registration_failure_marks_run_failed(monkeypatch):
    import sys
    db = MagicMock()
    db.create_run.return_value = 'watcher-run'
    db.register_file.side_effect = RuntimeError('database down')
    monkeypatch.setattr(watcher, 'db', db)
    monkeypatch.setattr(watcher.subprocess, 'run', MagicMock())
    monkeypatch.setattr(watcher.os, 'walk', lambda *args: [('raw/articles', [], ['a.md'])])
    monkeypatch.setitem(sys.modules, 'youtube_sync', MagicMock())
    with pytest.raises(RuntimeError, match='database down'):
        watcher.watch()
    assert db.complete_run.call_args.args[1] == 'failed'


def test_recovery_preserves_hidden_page(tmp_path, monkeypatch):
    from scripts import repair_source_mappings as repair
    (tmp_path / 'wiki/sources').mkdir(parents=True)
    source = tmp_path / 'raw/youtube/a.md'
    source.write_text('raw content')
    hidden = tmp_path / 'wiki/sources/.md'
    hidden.write_text('## Source\na.md\n\nOriginal generated summary')
    cursor = MagicMock()
    cursor.fetchall.return_value = [{'id': 1, 'file_path': 'raw/youtube/a.md', 'wiki_slug': None}]
    monkeypatch.setattr(repair, 'db', fake_database(cursor))
    monkeypatch.setattr(repair, 'build_wiki_index', MagicMock())
    monkeypatch.setattr(repair, 'rebuild_index', MagicMock())
    result = repair.repair()
    assert len(result['copied_hidden']) == 1
    copied = tmp_path / 'wiki/sources' / (result['copied_hidden'][0]['slug'] + '.md')
    assert copied.read_text() == hidden.read_text()
    assert hidden.exists()


def test_semantic_route_registered_before_server_starts(monkeypatch):
    import runpy
    from pathlib import Path
    import uvicorn
    started = []
    monkeypatch.setattr(uvicorn, 'run', lambda app, **kwargs: started.append({route.path for route in app.routes}))
    runpy.run_path(str(Path(ingest.__file__).with_name('runner_api.py')), run_name='__main__')
    assert '/semantic-search' in started[0]


def test_recovery_excludes_historical_csv(tmp_path, monkeypatch):
    from scripts import repair_source_mappings as repair
    (tmp_path / 'wiki/sources').mkdir(parents=True)
    (tmp_path / 'raw/youtube/history.csv').write_text('id,title\n1,Example')
    cursor = MagicMock()
    cursor.fetchall.return_value = [{'id': 5, 'file_path': 'raw/youtube/history.csv', 'wiki_slug': None}]
    monkeypatch.setattr(repair, 'db', fake_database(cursor))
    monkeypatch.setattr(repair, 'build_wiki_index', MagicMock())
    monkeypatch.setattr(repair, 'rebuild_index', MagicMock())
    result = repair.repair()
    assert result['excluded'] == [5]
    assert not list((tmp_path / 'wiki/sources').iterdir())


def test_client_configuration_failure_finishes_api_run(monkeypatch):
    db = MagicMock()
    db.register_file.return_value = 42
    monkeypatch.setattr(ingest, 'db', db)
    monkeypatch.setattr(ingest.genai, 'Client', MagicMock(side_effect=ValueError('API key missing')))
    with pytest.raises(ValueError, match='API key missing'):
        ingest.run_standalone('raw/a.md', None, 'model', 'api-run')
    assert db.complete_run.call_args.args[1] == 'failed'
