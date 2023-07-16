from notification_service.celery import app

from .mailing_sender import test_1, mailing_service, scheduler_service


@app.task
def test_task(task_id):
    res = test_1(task_id)
    return res


@app.task
def schedule_mailing(**kwargs):
    res = mailing_service(**kwargs)
    return res


@app.task
def periodic_task():
    scheduler_service()
