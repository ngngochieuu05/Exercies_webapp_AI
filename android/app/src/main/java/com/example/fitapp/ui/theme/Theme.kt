package com.example.fitapp.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = ElectricLime,
    secondary = ElectricCyan,
    tertiary = ActiveCoral,
    background = DarkBackground,
    surface = DarkSurface,
    surfaceVariant = DarkSurfaceVariant,
    onPrimary = DarkBackground,
    onSecondary = DarkBackground,
    onTertiary = TextWhite,
    onBackground = TextWhite,
    onSurface = TextWhite,
    onSurfaceVariant = TextGray,
    outline = BorderColor
)

@Composable
fun FitTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        content = content
    )
}
