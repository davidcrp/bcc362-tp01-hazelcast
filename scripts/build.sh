#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf build/classes
mkdir -p lib build/classes
if [ ! -f lib/hazelcast-5.6.0.jar ]; then
  curl -fL --retry 2 https://repo.maven.apache.org/maven2/com/hazelcast/hazelcast/5.6.0/hazelcast-5.6.0.jar -o lib/hazelcast-5.6.0.jar.tmp
  mv lib/hazelcast-5.6.0.jar.tmp lib/hazelcast-5.6.0.jar
fi
(cd lib && sha256sum -c SHA256SUMS)
javac --release 17 -encoding UTF-8 -cp lib/hazelcast-5.6.0.jar -d build/classes src/*.java
jar --create --file build/tp01.jar --main-class Main -C build/classes .
echo 'Compilação concluída.'
