FROM python:3.8-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get install -y wget
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get -y install ./google-chrome-stable_current_amd64.deb

WORKDIR /app
COPY logging.ini requirements.txt settings.toml ./
COPY src ./src
RUN python -m pip install -r requirements.txt

ENV PATH="${PATH}:/app/chrome"

CMD ["python", "-m", "src.main"]



FROM base as test

WORKDIR /app
COPY pytest.ini requirements-test.txt settings.test.toml ./
COPY tests ./tests
RUN python -m pip install -r requirements-test.txt

CMD ["python", "-m", "pytest"]


FROM base as release

WORKDIR /app
COPY lambda_function.py ./
RUN python -m pip install awslambdaric

CMD [ "python", "-m", "awslambdaric", "lambda_function.lambda_handler" ]
