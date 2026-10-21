from src.tasks.celery_app import celery_app, get_celery_settings


def test_celery_app_uses_redis_as_broker_and_backend():
    settings = get_celery_settings()
    assert celery_app.conf.broker_url == settings.redis_url
    assert celery_app.conf.result_backend == settings.redis_url


def test_celery_app_uses_json_serialization():
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.result_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]


def test_celery_app_tracks_task_start_and_has_time_limit():
    assert celery_app.conf.task_track_started is True
    assert celery_app.conf.task_time_limit == 5 * 60
