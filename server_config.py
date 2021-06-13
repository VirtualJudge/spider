import os

# RabbitMQ 相关的配置
MQ_USER = 'vj_user'
MQ_PASS = 'vj_pass'
MQ_HOST = '127.0.0.1'
MQ_PORT = 5672

# Redis 相关的配置
REDIS_USER = None
REDIS_PASS = None
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

# Celery 相关的配置
BROKER_URL = os.getenv(
    'BROKER_URL', f'amqp://{MQ_USER}:{MQ_PASS}@{MQ_HOST}:{MQ_PORT}/')

# 测试用的配置文件
ACCOUNTS_CONFIG = './accounts.yaml'
