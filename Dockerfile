# based on example from https://docs.docker.com/compose/gettingstarted/
FROM python:3.9-alpine
RUN apk add build-base cairo cairo-dev pkgconfig font-opensans tzdata
RUN apk --no-cache add msttcorefonts-installer fontconfig && \
    update-ms-fonts && \
    fc-cache -f

WORKDIR /usr/app

COPY pysvglabel/ ./pysvglabel/
WORKDIR /usr/app/pysvglabel
RUN pip install -r requirements.txt
WORKDIR /usr/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ext_art/ ./ext_art/

COPY *.py *.svg ./
COPY *.ics ./
COPY test/ ./test/

ENV FLASK_RUN_HOST=0.0.0.0
ENV TZ=America/Los_Angeles

EXPOSE 80
CMD ["flask", "run", "--port", "80"]
