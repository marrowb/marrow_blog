FROM python:3.13.3-slim-bookworm AS app-build
LABEL maintainer="Brandon Marrow <brandon.marrow@pm.me>"

WORKDIR /app

ARG UID=1000
ARG GID=1000

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential curl libsqlite3-dev \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && groupadd -g "${GID}" python \
  && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python \
  && chown python:python -R /app

COPY --from=ghcr.io/astral-sh/uv:0.6.9 /uv /uvx /usr/local/bin/

USER python

COPY --chown=python:python pyproject.toml uv.lock* ./
COPY --chown=python:python bin/ ./bin

ENV PYTHONUNBUFFERED="true" \
  PYTHONPATH="." \
  UV_COMPILE_BYTECODE=1 \
  UV_PROJECT_ENVIRONMENT="/home/python/.local" \
  PATH="${PATH}:/home/python/.local/bin" \
  USER="python"

RUN chmod 0755 bin/* && bin/uv-install

CMD ["bash"]

###############################################################################

FROM python:3.13.3-slim-bookworm AS app
LABEL maintainer="Brandon Marrow <brandon.marrow@pm.me>"

WORKDIR /app

ARG UID=1000
ARG GID=1000

RUN apt-get update \
  && apt-get install -y --no-install-recommends curl libsqlite3-dev \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && groupadd -g "${GID}" python \
  && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python \
  && chown python:python -R /app

USER python

ARG FLASK_DEBUG="false"
ENV FLASK_DEBUG="${FLASK_DEBUG}" \
  FLASK_APP="marrow_blog.app" \
  FLASK_SKIP_DOTENV="true" \
  PYTHONUNBUFFERED="true" \
  PYTHONPATH="." \
  UV_PROJECT_ENVIRONMENT="/home/python/.local" \
  PATH="${PATH}:/home/python/.local/bin" \
  USER="python"

COPY --chown=python:python --from=app-build /home/python/.local /home/python/.local
COPY --from=app-build /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/
COPY --chown=python:python . .

# Copy static assets to /public (for entrypoint to use at runtime)
COPY --chown=python:python ./assets/static /public

COPY --chown=python:python --from=app-build /home/python/.local /home/python/.local
COPY --from=app-build /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/
COPY --chown=python:python . .

# Create temporary symlink for flask digest compile (since assets are in /public)
RUN if [ "${FLASK_DEBUG}" != "true" ]; then \
  ln -s /public /app/public && cd /app && SECRET_KEY=dummy flask digest compile && rm -rf /app/public; fi


ENTRYPOINT ["/app/bin/docker-entrypoint-web"]

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "marrow_blog.app:create_app()"]
