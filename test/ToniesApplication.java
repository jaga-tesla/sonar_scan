package com.arizon.tonies;


import lombok.extern.slf4j.Slf4j;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.integration.annotation.IntegrationComponentScan;
import org.springframework.integration.config.EnableIntegration;
import javax.annotation.PostConstruct;
import java.util.TimeZone;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.context.annotation.ComponentScan;


@SpringBootApplication
@EnableJpaRepositories("com.arizon.tonies.repo")
@EntityScan("com.arizon.tonies.entity")
@ComponentScan("com.*")
@EnableIntegration
@IntegrationComponentScan
@Slf4j
//@EnableAutoConfiguration(exclude={DataSourceAutoConfiguration.class})
// @EnableScheduling
public class ToniesApplication extends SpringBootServletInitializer {


    public static void main(String[] args) {
        SpringApplication.run(ToniesApplication.class, args);
    }

    @PostConstruct
    public void init(){
        TimeZone.setDefault(TimeZone.getTimeZone("America/New_York"));
    }
}
