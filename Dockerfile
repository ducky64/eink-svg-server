# based on example from https://docs.docker.com/compose/gettingstarted/
FROM python:3.9-alpine

WORKDIR /usr/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY pysvglabel/ ./pysvglabel/

COPY *.py *.svg ./
ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 80
CMD ["flask", "run", "--port", "80"]
