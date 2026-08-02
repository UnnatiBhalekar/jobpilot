package com.jobpilot.jobpilot.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Entity
@Table(name = "education")
@Getter
@Setter
@NoArgsConstructor
public class Education {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "resume_id", nullable = false)
    private Resume resume;

    @Column(nullable = false)
    private String institution;

    @Column(nullable = false)
    private String degree;

    private String location;

    @Column(name = "end_date")
    private LocalDate endDate;

    private String grade;

    @Column(name = "display_order", nullable = false)
    private int displayOrder = 0;
}
