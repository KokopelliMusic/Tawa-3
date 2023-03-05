FROM python:3.10-slim as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV DYLD_LIBRARY_PATH "/usr/local/mysql/lib:$PATH"


FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update 
RUN apt-get install -y gcc musl-dev default-libmysqlclient-dev python3-dev libmariadb-dev
RUN pip3 install mysqlclient mysql

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy


FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

RUN apt-get update
RUN apt-get install -y default-libmysqlclient-dev libmariadb-dev

# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Install application into container
COPY . .

# Run the application
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

# FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

# ENV LANG C.UTF-8
# ENV LC_ALL C.UTF-8
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONFAULTHANDLER 1

# EXPOSE 8000
# WORKDIR /app 
# COPY Pipfile /app
# COPY Pipfile.lock /app
# RUN pip3 install pipenv
# RUN apk add gcc musl-dev mysql-client mariadb-connector-c-dev
# RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
# COPY . /app 
# ENTRYPOINT ["python3"] 
# CMD ["manage.py", "runserver", "0.0.0.0:8000"]

# FROM builder as dev-envs
# RUN <<EOF
# apk update
# apk add git
# EOF

# RUN <<EOF
# addgroup -S docker
# adduser -S --shell /bin/bash --ingroup docker vscode
# EOF
# # install Docker tools (cli, buildx, compose)
# COPY --from=gloursdocker/docker / /
# CMD ["manage.py", "runserver", "0.0.0.0:8000"]