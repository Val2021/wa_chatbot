
FROM python:3.10.12-buster

WORKDIR /src

COPY requirements.txt requirements.txt

RUN apt update && apt install -y \
    && pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY src /src
COPY .env /src/.env

EXPOSE 8501

CMD ["streamlit", "run", "Home.py"]
