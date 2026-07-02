package com.example.fitapp.ui.components

import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
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

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun ExerciseCard(exercise: Exercise) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = !expanded }
            .animateContentSize(),
        elevation = CardDefaults.cardElevation(defaultElevation = 3.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Exercise Image/Gif
                if (!exercise.gif_url.isNullOrEmpty()) {
                    AsyncImage(
                        model = exercise.gif_url,
                        contentDescription = exercise.name,
                        modifier = Modifier
                            .size(72.dp)
                            .clip(RoundedCornerShape(8.dp)),
                        contentScale = ContentScale.Crop
                    )
                } else {
                    Surface(
                        modifier = Modifier
                            .size(72.dp)
                            .clip(RoundedCornerShape(8.dp)),
                        color = MaterialTheme.colorScheme.surfaceVariant
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Text(
                                text = "💪",
                                style = MaterialTheme.typography.headlineMedium
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.width(16.dp))

                // Exercise Info
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = exercise.name.replaceFirstChar { it.uppercase() },
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = "Nhóm cơ: ${exercise.muscle_group.replaceFirstChar { it.uppercase() }}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Chips row (Wrap in FlowRow to prevent clipping)
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(6.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                SuggestionChip(
                    onClick = {},
                    label = { Text(translateCategory(exercise.category)) }
                )
                SuggestionChip(
                    onClick = {},
                    label = { Text(translateEquipment(exercise.equipment)) }
                )
                SuggestionChip(
                    onClick = {},
                    label = { Text("Mục tiêu: ${exercise.target.replaceFirstChar { it.uppercase() }}") },
                    colors = SuggestionChipDefaults.suggestionChipColors(
                        labelColor = MaterialTheme.colorScheme.secondary
                    )
                )
            }

            // Expanded view for instructions
            if (expanded) {
                Spacer(modifier = Modifier.height(12.dp))
                HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
                Spacer(modifier = Modifier.height(12.dp))

                Text(
                    text = "Hướng dẫn thực hiện:",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Spacer(modifier = Modifier.height(6.dp))

                val instructions = exercise.instructions["en"]
                if (!instructions.isNullOrEmpty()) {
                    Text(
                        text = instructions,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                } else {
                    Text(
                        text = "Chưa có hướng dẫn cho bài tập này.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

