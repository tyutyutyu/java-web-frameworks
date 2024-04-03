package com.tyutyutyu.jwf;

import io.quarkus.runtime.Quarkus;
import io.quarkus.runtime.QuarkusApplication;
import io.quarkus.runtime.annotations.QuarkusMain;

@QuarkusMain
public class QuarkusMavenApplication {

    public static void main(String... args) {
        System.out.println("[JWF] JAVA STARTED: " + System.currentTimeMillis());
        Quarkus.run(MyApp.class, args);
    }

    public static class MyApp implements QuarkusApplication {

        @Override
        public int run(String... args) {
            Quarkus.waitForExit();
            return 0;
        }
    }

}
