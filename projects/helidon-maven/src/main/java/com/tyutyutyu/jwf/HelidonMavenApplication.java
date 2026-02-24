package com.tyutyutyu.jwf;

import io.helidon.webserver.WebServer;
import io.helidon.webserver.http.HttpRouting;

public class HelidonMavenApplication {

    public static void main(String[] args) {
        System.out.println("[JWF] JAVA STARTED: " + System.currentTimeMillis());

        WebServer server = WebServer.builder()
                .addRouting(HttpRouting.builder()
                        .get("/hello", (req, res) -> res.send("Hello from Helidon")))
                .build()
                .start();

        System.out.println("[JWF] FRAMEWORK STARTED: " + System.currentTimeMillis());

        System.out.println("[JWF] START FRAMEWORK SHUTDOWN: " + System.currentTimeMillis());
        server.stop();
    }

}
