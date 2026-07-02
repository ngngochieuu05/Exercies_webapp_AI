package com.example.fitapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.activity.viewModels
import com.example.fitapp.ui.ExerciseListScreen
import com.example.fitapp.ui.ExerciseViewModel

class MainActivity : ComponentActivity() {
    private val viewModel: ExerciseViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                ExerciseListScreen(viewModel)
            }
        }
    }
}
