package com.jobpilot.jobpilot.controller;

import com.jobpilot.jobpilot.dto.UserCreateRequest;
import com.jobpilot.jobpilot.dto.UserResponse;
import com.jobpilot.jobpilot.entity.User;
import com.jobpilot.jobpilot.repository.UserRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserRepository userRepository;

    public UserController(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUser(@PathVariable Long id) {
        return userRepository.findById(id)
            .map(UserResponse::from)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<UserResponse> createUser(@jakarta.validation.Valid @RequestBody UserCreateRequest request) {
        User user = new User();
        user.setEmail(request.email());
        user.setName(request.name());
        // NOTE: storing the raw password directly for now — this is NOT secure.
        // We'll replace this with proper password hashing (BCrypt) once we
        // build real authentication. Do not treat this as production-ready.
        user.setPasswordHash(request.password());

        User saved = userRepository.save(user);
        return ResponseEntity.ok(UserResponse.from(saved));
    }
}
