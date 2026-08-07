package com.jobpilot.jobpilot.dto;

import com.jobpilot.jobpilot.entity.User;

public record UserResponse(
    Long id,
    String email,
    String name,
    String location
) {
    public static UserResponse from(User user) {
        return new UserResponse(
            user.getId(),
            user.getEmail(),
            user.getName(),
            user.getLocation()
        );
    }
}
