FROM tiangolo/uwsgi-nginx-flask:python3.7
ARG REQUIREMENTS
RUN apt-get update && apt-get -y install libffi-dev gcc python3-dev libffi-dev libssl-dev libxml2-dev libxmlsec1-dev libxmlsec1-openssl

WORKDIR /app
COPY requirements.txt /app/
RUN echo $REQUIREMENTS
RUN pip install -r $REQUIREMENTS
COPY ./lti/ /app/