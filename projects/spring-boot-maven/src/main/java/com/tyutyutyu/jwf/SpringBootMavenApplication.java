package com.tyutyutyu.jwf;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.event.EventListener;

@SpringBootApplication
public class SpringBootMavenApplication {

    @Autowired
    private ConfigurableApplicationContext applicationContext;

    public static void main(String[] args) {
        System.out.println("[JWF] JAVA STARTED: " + System.currentTimeMillis());
        SpringApplication.run(SpringBootMavenApplication.class, args);
    }

    @EventListener(ApplicationReadyEvent.class)
    public void doSomethingAfterStartup() {
        System.out.println("[JWF] FRAMEWORK STARTED: " + System.currentTimeMillis());

        System.out.println("[JWF] START FRAMEWORK SHUTDOWN: " + System.currentTimeMillis());
        SpringApplication.exit(applicationContext);
    }

}
