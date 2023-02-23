FROM python:3.10-slim as base

WORKDIR /app
RUN apt-get update && apt-get install -y git curl unzip

RUN python -m pip install --upgrade pip

COPY requirements.txt ./
RUN python -m pip install -r requirements.txt && \
	rm -rf "./requirements.txt"

FROM base as release
COPY . ./
ENTRYPOINT [ "python","-m", "awslambdaric" ]
CMD [ "AWS.app.lambda_handler" ]

FROM base as test-deps
COPY requirements-test.txt ./
RUN pip install -r requirements-test.txt && \
	rm -rf "./requirements-test.txt"

FROM test-deps as test
COPY . ./
ENTRYPOINT [ "python", "-m", "pytest" ]