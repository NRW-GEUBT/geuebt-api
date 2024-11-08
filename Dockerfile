FROM python:3.10-slim as fastapi

WORKDIR /

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade --requirement ./requirements.txt

COPY ./app/server ./server

FROM fastapi as backend

EXPOSE 8081

CMD ["uvicorn", "server.app:app --host 0.0.0.0 --port 8081"]
