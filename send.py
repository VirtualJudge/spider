from celery import Celery

from server_config import BROKER_URL

app = Celery('spider')
app.conf.update(
    broker_url=BROKER_URL,
    enable_utc=True,
    task_serializer='json',
)


@app.task(name="problem")
def send_problem(local_pid: int, remote_oj: str, remote_id: str):
    print(local_pid, remote_oj, remote_id)


@app.task(name="submission")
def send_submission(local_id: int, remote_oj: str, remote_id: str, language: str, code: str):
    print(local_id, remote_oj, remote_id, language, code)


if __name__ == '__main__':
    send_submission.apply_async(
        args=[1, 'HDU', '1000'],
        queue='requests'
    )
