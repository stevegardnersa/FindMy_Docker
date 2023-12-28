FROM python:3.11-bookworm

RUN apt update && apt install -y sqlite3
RUN pip install pypush srp cryptography requests pbkdf2 pycryptodomex

WORKDIR /app
COPY . .

CMD /app/request_reports.py