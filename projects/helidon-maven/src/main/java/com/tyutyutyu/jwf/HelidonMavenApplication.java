package com.tyutyutyu.jwf;

import io.helidon.webserver.WebServer;

public class HelidonMavenApplication {

    public static void main(String[] args) {
        System.out.println("[JWF] JAVA STARTED: " + System.currentTimeMillis());

        WebServer server = WebServer.builder()
                .routing(routing -> routing
                        .get("/hello", (req, res) -> res.send("Hello from Helidon")))
                .build();

        server.start()
                .thenApply(ws -> {
                    System.out.println("[JWF] FRAMEWORK STARTED: " + System.currentTimeMillis());
                    System.out.println("[JWF] START FRAMEWORK SHUTDOWN: " + System.currentTimeMillis());
                    return ws;
                })
                .thenCompose(WebServer::shutdown)
                .toCompletableFuture()
                .join();
    }

}
