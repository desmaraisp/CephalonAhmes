FROM python:3.9.14-slim as base

WORKDIR /app
RUN apt-get update && apt-get install -y git

RUN python -m pip install --upgrade pip

COPY requirements.txt ./
RUN python -m pip install -r requirements.txt --force-reinstall && \
	rm -rf "./requirements.txt"

FROM base as test-deps
COPY requirements-test.txt ./
RUN pip install -r requirements-test.txt --force-reinstall && \
	rm -rf "./requirements-test.txt"

FROM test-deps as dev
COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt --force-reinstall && \
	rm -rf "./requirements-dev.txt"

FROM base as release
COPY . ./
ENTRYPOINT [ "python","-m", "awslambdaric" ]
CMD [ "app.lambda_handler" ]

FROM test-deps as test
COPY . ./
ENTRYPOINT [ "python", "-m", "pytest", "./tests" ]
