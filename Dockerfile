FROM python:3.9.5-buster

LABEL maintainer="xudian.cn@gmail.com"

ADD . /app
WORKDIR /app
RUN useradd -ms /bin/bash -u 1000 runner
RUN chown -R runner /app
USER runner
RUN pip3 install --no-cache-dir -r requirements.txt --no-warn-script-location
RUN echo "PATH=$PATH:/home/runner/.local/bin" >> /home/runner/.bashrc
CMD ["bash", "-c", "celery -A tasks worker -l info -Q requests -n worker@spider --concurrency 8"]