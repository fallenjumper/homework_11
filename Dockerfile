FROM python:3.9.7-slim-bullseye

WORKDIR /usr/src/app

COPY /src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && mkdir /allure-results \
    && chmod -R 777 /allure-results

COPY /src/ .

ENTRYPOINT ["pytest"]
