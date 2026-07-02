package com.example.fitapp.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.fitapp.data.model.Exercise

fun translateCategory(cat: String): String {
    return when(cat.lowercase().trim()) {
        "waist" -> "Cơ bụng / Vòng eo"
        "upper arms" -> "Bắp tay (Trước/Sau)"
        "lower arms" -> "Cẳng tay"
        "upper legs" -> "Đùi / Chân trên"
        "lower legs" -> "Bắp chân / Chân dưới"
        "back" -> "Cơ lưng"
        "chest" -> "Cơ ngực"
        "shoulders" -> "Cơ vai"
        "cardio" -> "Cardio / Tim mạch"
        "neck" -> "Cơ cổ"
        else -> cat.replaceFirstChar { it.uppercase() }
    }
}

fun translateEquipment(equip: String): String {
    return when(equip.lowercase().trim()) {
        "body weight" -> "Trọng lượng cơ thể"
        "dumbbell" -> "Tạ đơn (Dumbbell)"
        "barbell" -> "Tạ đòn (Barbell)"
        "cable" -> "Máy kéo cáp"
        "leverage machine" -> "Máy đòn bẩy"
        "band" -> "Dây kháng lực"
        "smith machine" -> "Máy Smith"
        "kettlebell" -> "Tạ ấm (Kettlebell)"
        "weighted" -> "Tạ thêm"
        "stability ball" -> "Bóng tập yoga"
        "ez barbell" -> "Thanh tạ EZ"
        else -> equip.replaceFirstChar { it.uppercase() }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExerciseListScreen(viewModel: ExerciseViewModel) {
    val exercises by viewModel.exercises.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Thư viện Bài tập") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            if (isLoading) {
                Column(
                    modifier = Modifier.align(Alignment.Center),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Đang tải dữ liệu...", style = MaterialTheme.typography.bodyMedium)
                }
            } else if (error != null) {
                Column(
                    modifier = Modifier.align(Alignment.Center),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(error!!, color = MaterialTheme.colorScheme.error)
                    Spacer(modifier = Modifier.height(8.dp))
                    Button(onClick = { viewModel.fetchExercises() }) {
                        Text("Thử lại")
                    }
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(exercises) { exercise ->
                        ExerciseCard(exercise)
                    }
                }
            }
        }
    }
}

@Composable
fun ExerciseCard(exercise: Exercise) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = exercise.name.replaceFirstChar { it.uppercase() },
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(4.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SuggestionChip(onClick = {}, label = { Text(translateCategory(exercise.category)) })
                SuggestionChip(onClick = {}, label = { Text(translateEquipment(exercise.equipment)) })
            }
        }
    }
}
