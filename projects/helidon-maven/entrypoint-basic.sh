#!/usr/bin/env sh

set -e

echo "[JWF] STARTING JAVA: $(date +%s%N)"
time -v -o time.out java -jar /app.jar
echo "[JWF] JAVA STOPPED: $(date +%s%N)"

echo "!!!"
cat time.out
echo "!!!"
