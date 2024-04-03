package com.tyutyutyu.jwf;

import io.micronaut.context.ApplicationContext;
import io.micronaut.runtime.event.annotation.EventListener;
import io.micronaut.runtime.server.event.ServerStartupEvent;
import jakarta.inject.Singleton;

import java.util.concurrent.CompletableFuture;

@Singleton
public class ShutdownManager {

    private final ApplicationContext applicationContext;

    public ShutdownManager(ApplicationContext applicationContext) {
        this.applicationContext = applicationContext;
    }

    @EventListener
    public void onStartup(ServerStartupEvent event) {
        System.out.println("[JWF] FRAMEWORK STARTED: " + System.currentTimeMillis());

        CompletableFuture.runAsync(() -> {
            System.out.println("[JWF] START FRAMEWORK SHUTDOWN: " + System.currentTimeMillis());
            applicationContext.stop();
        });
    }

}
