package com.jobpilot.jobpilot.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

// TEMPORARY: authentication isn't built yet. This disables Spring Security's
// default lockdown so we can build and test endpoints freely. We will
// replace this with real JWT-based auth once the User/Auth endpoints exist —
// do not ship this configuration as-is.
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth.anyRequest().permitAll());
        return http.build();
    }
}
