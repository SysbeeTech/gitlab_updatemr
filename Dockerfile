FROM python:3.12.0-slim-bookworm
MAINTAINER "branko@sysbee.net"
LABEL org.opencontainers.image.source https://github.com/sysbeetech/gitlab_updatemr
COPY --chown=1000:1000 ./app/ /app
RUN pip install -r /app/requirements.txt
WORKDIR /app
USER 1000
CMD ["./update_mr.py"]
