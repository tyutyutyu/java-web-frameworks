package com.tyutyutyu.jwf;

import io.quarkus.runtime.Quarkus;
import io.quarkus.runtime.StartupEvent;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;

@ApplicationScoped
public class AppLifecycleBean {

    void onStart(@Observes StartupEvent ev) {
        System.out.println("[JWF] FRAMEWORK STARTED: " + System.currentTimeMillis());

        System.out.println("[JWF] START FRAMEWORK SHUTDOWN: " + System.currentTimeMillis());
        Quarkus.asyncExit();
    }

}
