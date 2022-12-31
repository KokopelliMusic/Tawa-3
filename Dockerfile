FROM python:3.10-buster as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base as python-deps

# Install pipenv and compilation dependencies
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends gcc python3-setuptools
RUN pip install --upgrade setuptools
RUN pip install pipenv pytest

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy


FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Install application into container
COPY . .

EXPOSE 8000

# Run the application
ENTRYPOINT ["daphne", "-b", "0.0.0.0", "-p", "8000", "--proxy-headers", "tawa3.asgi:application"]