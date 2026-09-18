FROM eclipse-temurin:17-jdk-jammy AS build
WORKDIR /app
COPY lib/hazelcast-5.6.0.jar lib/hazelcast-5.6.0.jar
COPY src src
RUN mkdir -p build/classes && javac --release 17 -encoding UTF-8 -cp lib/hazelcast-5.6.0.jar -d build/classes src/main/java/br/edu/ufop/*.java && jar --create --file build/tp01.jar -C build/classes .
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app
COPY --from=build /app/lib lib
COPY --from=build /app/build build
ENTRYPOINT ["java", "-Xms128m", "-Xmx768m", "-XX:ActiveProcessorCount=2", "-cp", "build/tp01.jar:lib/*", "br.edu.ufop.Main"]
