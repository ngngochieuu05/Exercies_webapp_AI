package com.example.fitapp.data.model

data class ExerciseResponse(
    val data: List<Exercise>,
    val total: Int,
    val page: Int,
    val limit: Int,
    val totalPages: Int
)

data class Exercise(
    val id: String,
    val name: String,
    val category: String,
    val body_part: String,
    val equipment: String,
    val instructions: Map<String, String>,
    val muscle_group: String,
    val secondary_muscles: List<String>,
    val target: String,
    val image: String?,
    val gif_url: String?
)
