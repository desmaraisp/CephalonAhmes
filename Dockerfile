FROM python:3.14-slim AS base

WORKDIR /app
RUN apt-get update && apt-get install -y git curl unzip

RUN python -m pip install --upgrade pip

COPY requirements.txt ./
RUN python -m pip install -r requirements.txt && \
	rm -rf "./requirements.txt"

FROM base AS type-check-deps
COPY requirements-dev.txt ./
RUN python -m pip install -r requirements-dev.txt && \
	rm -rf "./requirements-dev.txt"

FROM type-check-deps AS type-check

COPY . ./
ENTRYPOINT [ "python", "-m", "mypy", "src" ]

FROM base AS release
COPY . ./
ENTRYPOINT [ "python","-m", "awslambdaric" ]
CMD [ "AWS.app.lambda_handler" ]

FROM base AS test-deps
COPY requirements-test.txt ./
RUN pip install -r requirements-test.txt && \
	rm -rf "./requirements-test.txt"

FROM test-deps AS test
COPY . ./
ENTRYPOINT [ "python", "-m", "pytest" ]