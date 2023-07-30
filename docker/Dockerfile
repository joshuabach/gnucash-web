# docker build -t gnucash-web .
# docker run --rm -p 8080:8080 --name gnucash-web --add-host=host.docker.internal:host-gateway gnucash-web

# not using python:alpine so i don't have to compile uwsgi
FROM alpine
RUN apk add --no-cache python3 py3-pip
CMD ["uwsgi", "--ini", "/etc/gnucash-web/uwsgi.ini"]
RUN apk add --no-cache uwsgi uwsgi-python3
RUN pip install GnuCash-Web 'Flask<2.3.0'
RUN pip install psycopg2-binary
RUN apk add --no-cache py3-mysqlclient
COPY config.py /etc/gnucash-web/config.py
COPY uwsgi.ini /etc/gnucash-web/uwsgi.ini
ENV LOG_LEVEL 'WARNING'
ENV DB_DRIVER 'mysql'
ENV DB_HOST 'host.docker.internal'
ENV DB_NAME 'gnucash'
ENV AUTH_MECHANISM 'passthrough'
ENV TRANSACTION_PAGE_LENGTH 25
ENV PRESELECTED_CONTRA_ACCOUNT 'Expenses:Groceries'
