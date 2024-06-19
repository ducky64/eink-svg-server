# based on example from https://docs.docker.com/compose/gettingstarted/
FROM python:3.9-alpine
RUN apk add build-base cairo cairo-dev pkgconfig font-opensans tzdata

WORKDIR /usr/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY pysvglabel/ ./pysvglabel/
COPY ext_art/ ./ext_art/

COPY *.py *.svg ./
ENV FLASK_RUN_HOST=0.0.0.0
ENV TZ=America/Los_Angeles

EXPOSE 80
CMD ["flask", "run", "--port", "80"]
