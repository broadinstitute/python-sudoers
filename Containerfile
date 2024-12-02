FROM docker.io/node:bookworm AS prettier-install
RUN yarn add prettier@3

FROM python:3.12-slim

ARG LOCAL_BIN=/root/.local/bin
ENV PATH=$LOCAL_BIN:$PATH

# Install prettier
RUN mkdir -p $LOCAL_BIN
COPY --from=prettier-install /usr/local/bin/node $LOCAL_BIN
COPY --from=prettier-install /node_modules/prettier /prettier
RUN ln -s /prettier/bin/prettier.cjs $LOCAL_BIN/prettier

COPY poetry.lock pyproject.toml README.md /working/

WORKDIR /working

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -yq curl make \
    && pip install -U pip poetry \
    && poetry install --no-root \
    && rm -rf /tmp/* \
    && rm -rf /var/cache/apt/* \
    && rm -rf /var/tmp/*

ENTRYPOINT ["poetry", "run"]

CMD ["bash"]
