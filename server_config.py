import os

# RabbitMQ 相关的配置
MQ_USER = os.getenv('MQ_USER', 'vj_user')
MQ_PASS = os.getenv('MQ_PASS', 'vj_pass')
MQ_HOST = os.getenv('MQ_HOST', '127.0.0.1')
MQ_PORT = os.getenv('MQ_PORT', 5672)

# Redis 相关的配置
REDIS_USER = os.getenv('REDIS_USER', None)
REDIS_PASS = os.getenv('REDIS_PASS', None)
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = 4
# Celery 相关的配置
BROKER_URL = f'amqp://{MQ_USER}:{MQ_PASS}@{MQ_HOST}:{MQ_PORT}/'

# 测试用的配置文件
ACCOUNTS_CONFIG = './accounts.yaml'
