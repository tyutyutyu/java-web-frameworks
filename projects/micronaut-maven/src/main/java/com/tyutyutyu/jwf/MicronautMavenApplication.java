package com.tyutyutyu.jwf;

import io.micronaut.runtime.Micronaut;

public class MicronautMavenApplication {

    public static void main(String[] args) {
        System.out.println("[JWF] JAVA STARTED: " + System.currentTimeMillis());
        Micronaut.build(args)
                .banner(false)
                .start();
    }

}