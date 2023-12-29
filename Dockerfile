FROM python:3.11-bookworm

RUN pip install pypush srp cryptography requests pbkdf2 pycryptodomex flask

WORKDIR /app
COPY . .

CMD /app/server.py