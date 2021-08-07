from celery import Celery

from server_config import BROKER_URL
from tasks import retrieve_problem_task, result_problem_task, sync_problem_list

app = Celery('platforms')
app.conf.update(
    broker_url=BROKER_URL,
    enable_utc=True,
    task_serializer='json',
)

if __name__ == '__main__':
    sync_problem_list.apply_async(
        args=['HDU', ['1000', ]],
        queue='requests'
    )

