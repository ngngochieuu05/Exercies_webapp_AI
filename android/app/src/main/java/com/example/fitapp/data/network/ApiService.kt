package com.example.fitapp.data.network

import com.example.fitapp.data.model.ExerciseResponse
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Query

interface ApiService {
    @GET("exercises")
    suspend fun getExercises(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20
    ): ExerciseResponse

    companion object {
        private const val BASE_URL = "http://10.0.2.2:8000/"

        val instance: ApiService by lazy {
            Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .create(ApiService::class.java)
        }
    }
}
