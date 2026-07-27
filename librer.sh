#!/bin/sh

cd /app/share/librer || exit 1
exec python3 /app/share/librer/librer.py "$@"
