FROM python:3.9-slim

LABEL vendor=neon.ai \
    ai.neon.name="neon-llm-chatgpt"

ENV OVOS_CONFIG_BASE_FOLDER=neon
ENV OVOS_CONFIG_FILENAME=diana.yaml
ENV OVOS_DEFAULT_CONFIG=/opt/neon/diana.yaml
ENV XDG_CONFIG_HOME=/config
ENV CHATBOT_VERSION=v2
ENV HEALTHCHECK_PORT=8000

COPY docker_overlay/ /
RUN apt-get update && apt-get install -y git
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir /app

HEALTHCHECK CMD "/opt/neon/healthcheck.sh"
CMD [ "neon-llm-chatgpt" ]
