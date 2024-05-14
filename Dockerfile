FROM python:3.11-alpine AS builder
LABEL authors="freddo"

WORKDIR /srv/

RUN apk add \
      gcc \
      musl-dev \
      mariadb-dev \
      python3-dev \
      libpq-dev

RUN pip wheel --no-cache-dir --wheel-dir /wheels mysql pycryptodome psycopg2

FROM python:3.11-alpine

WORKDIR /srv/

COPY ./src/ ./
COPY ./README.md ./
COPY --from=builder /wheels /wheels

RUN apk add libpq  mariadb-client
RUN pip install -v --no-cache /wheels/* .[pgsql,mysql,redis] gunicorn
RUN rm -r /wheels

EXPOSE 8000

ENV SECRET_KEY='00000000000000000000000000000000'
ENV LOG_LEVEL='WARN'
ENV DB_DRIVER='sqlite'
ENV DB_NAME='/gnucash.sqlite'
ENV DB_HOST='localhost'
ENV AUTH_MECHANISM=''
ENV TRANSACTION_PAGE_LENGTH=25
ENV PRESELECTED_CONTRA_ACCOUNT=''

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0", "gnucash_web.wsgi:app"]
