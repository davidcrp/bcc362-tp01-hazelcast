#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec java -Xms128m -Xmx768m -XX:ActiveProcessorCount=2 -cp 'build/tp01.jar:lib/*' Main "$@"
