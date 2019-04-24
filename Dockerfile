FROM python:3.6-alpine

COPY Pipfile* /usr/src/

WORKDIR /usr/src

RUN apk update \
    && apk add bash curl gcc git libxml2-dev libxslt-dev musl-dev \
    && pip install pipenv==2018.11.26 --upgrade \
    && curl -o /tmp/circlecli.sh -fLSs https://circle.ci/cli \
    && bash /tmp/circlecli.sh \
    && pipenv install --dev --system \
    && rm -f /etc/localtime \
    && ln -s /usr/share/zoneinfo/America/New_York /etc/localtime \
    && rm -rf /tmp/* \
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/tmp/*

CMD ["bash", "-l"]
