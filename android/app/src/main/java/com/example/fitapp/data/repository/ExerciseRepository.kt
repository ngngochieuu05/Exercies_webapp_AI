package com.example.fitapp.data.repository

import com.example.fitapp.data.model.ExerciseResponse
import com.example.fitapp.data.network.ApiService

class ExerciseRepository(private val apiService: ApiService = ApiService.instance) {
    suspend fun getExercises(page: Int, limit: Int): ExerciseResponse {
        return apiService.getExercises(page, limit)
    }
}
