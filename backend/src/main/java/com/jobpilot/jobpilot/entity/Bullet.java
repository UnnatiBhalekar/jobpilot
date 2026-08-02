package com.jobpilot.jobpilot.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "bullets")
@Getter
@Setter
@NoArgsConstructor
public class Bullet {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "experience_id")
    private Experience experience;   // nullable — set only if this bullet belongs to an experience

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id")
    private Project project;         // nullable — set only if this bullet belongs to a project

    @Column(nullable = false, columnDefinition = "TEXT")
    private String text;

    @Column(name = "display_order", nullable = false)
    private int displayOrder = 0;

    @ManyToMany
    @JoinTable(
        name = "bullet_tags",
        joinColumns = @JoinColumn(name = "bullet_id"),
        inverseJoinColumns = @JoinColumn(name = "tag_id")
    )
    private Set<Tag> tags = new HashSet<>();

    // Mirrors the database's chk_bullet_single_parent CHECK constraint,
    // but catches the mistake here in Java with a clear message,
    // rather than letting it fail deep inside a raw SQL exception.
    @PrePersist
    @PreUpdate
    private void validateExactlyOneParent() {
        boolean hasExperience = experience != null;
        boolean hasProject = project != null;
        if (hasExperience == hasProject) {
            throw new IllegalStateException(
                "A Bullet must belong to exactly one of Experience or Project, not both or neither."
            );
        }
    }
}
