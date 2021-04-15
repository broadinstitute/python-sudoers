FROM python:3.8-slim

COPY poetry.lock pyproject.toml README.md /usr/src/

WORKDIR /usr/src

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -yq curl \
    && pip install -U pip poetry \
    && poetry install \
    && rm -f /etc/localtime \
    && ln -s /usr/share/zoneinfo/America/New_York /etc/localtime \
    && rm -rf /tmp/* \
    && rm -rf /var/cache/apt/* \
    && rm -rf /var/tmp/*

ENTRYPOINT ["poetry", "run"]

CMD ["bash"]
