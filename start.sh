#!/bin/bash

if [ ! -f './data/reports.db' ]; then
  sqlite3 ./data/reports.db 'CREATE TABLE reports (id_short TEXT, timestamp INTEGER, datePublished INTEGER, payload TEXT, id TEXT, statusCode INTEGER, PRIMARY KEY(id_short,timestamp))'
fi

./request_reports.py
