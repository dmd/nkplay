#!/usr/bin/python3
"""CGI script: validates GET params and appends to a CSV.

Expected query string: ?p=<playlist>&h=<hostname>
  p — integer, 0 <= p < 1000
  h — 1-15 chars, [A-Za-z0-9-]

CSV columns: iso_utc_timestamp, playlist, hostname
"""
import csv
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import parse_qs

CSV_PATH = 'nkplay-log.csv'

HOST_RE = re.compile(r'^[A-Za-z0-9-]{1,15}$')


def respond(status, body=''):
    sys.stdout.write('Status: ' + status + '\r\n')
    sys.stdout.write('Content-Type: text/plain\r\n\r\n')
    sys.stdout.write(body)


def main():
    params = parse_qs(os.environ.get('QUERY_STRING', ''))
    p = (params.get('p') or [''])[0]
    h = (params.get('h') or [''])[0]

    if not p.isdigit() or int(p) >= 1000:
        respond('400 Bad Request', 'bad p')
        return
    if not HOST_RE.match(h):
        respond('400 Bad Request', 'bad h')
        return

    ts = datetime.now(timezone.utc).isoformat()
    with open(CSV_PATH, 'a', newline='') as f:
        csv.writer(f).writerow([ts, p, h])

    respond('200 OK', 'ok')


if __name__ == '__main__':
    main()
