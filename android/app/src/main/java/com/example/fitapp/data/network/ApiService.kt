package com.example.fitapp.data.network

import com.example.fitapp.data.model.ExerciseResponse
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body
import retrofit2.http.Query


data class ChatRequest(val message: String)
data class ChatResponse(val reply: String, val a2ui_messages: List<String>?)

interface ApiService {
    @GET("exercises")
    suspend fun getExercises(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20
    ): ExerciseResponse

    @GET("a2ui/dashboard")
    suspend fun getDashboardMessages(): List<String>

    @POST("a2ui/chat")
    suspend fun sendChatMessage(@Body request: ChatRequest): ChatResponse

    companion object {
        private const val BASE_URL = "http://192.168.1.12:8000/"

        val instance: ApiService by lazy {
            Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .create(ApiService::class.java)
        }
    }
}

