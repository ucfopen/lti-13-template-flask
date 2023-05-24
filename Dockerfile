FROM agostof/uwsgi-nginx-flask:python3.8
ARG REQUIREMENTS
RUN apt-get update && apt-get -y install ca-certificates libffi-dev gcc python3-dev libffi-dev libssl-dev libxml2-dev libxmlsec1-dev libxmlsec1-openssl

WORKDIR /app
COPY requirements.txt /app/
COPY test_requirements.txt /app/
RUN echo $REQUIREMENTS
RUN pip install -r $REQUIREMENTS
COPY ./lti/ /app/
