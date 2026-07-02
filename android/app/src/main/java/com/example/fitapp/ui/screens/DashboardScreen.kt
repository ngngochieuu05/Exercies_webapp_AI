package com.example.fitapp.ui.screens

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.example.fitapp.data.network.ApiService
import kotlinx.coroutines.launch
import org.a2ui.compose.rendering.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val renderer = remember { A2UIRenderer() }
    var isLoading by remember { mutableStateOf(true) }
    var errorMsg by remember { mutableStateOf<String?>(null) }

    val actionHandler = remember {
        object : ActionHandler {
            override fun onAction(surfaceId: String, actionName: String, actionContext: Map<String, Any>) {
                Toast.makeText(context, "Action: $actionName", Toast.LENGTH_SHORT).show()
            }
            override fun openUrl(url: String) {}
            override fun showToast(message: String) {
                Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
            }
        }
    }

    LaunchedEffect(Unit) {
        renderer.setActionHandler(actionHandler)
        try {
            val messages = ApiService.instance.getDashboardMessages()
            messages.forEach { msg ->
                renderer.processMessage(msg)
            }
            isLoading = false
        } catch (e: Exception) {
            errorMsg = "Không thể tải dashboard: ${e.message}"
            isLoading = false
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Thể trạng & Thống kê") },
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
                .padding(16.dp)
        ) {
            if (isLoading) {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
            } else if (errorMsg != null) {
                Column(
                    modifier = Modifier.align(Alignment.Center),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(errorMsg!!, color = MaterialTheme.colorScheme.error)
                    Spacer(modifier = Modifier.height(8.dp))
                    Button(onClick = {
                        isLoading = true
                        errorMsg = null
                        coroutineScope.launch {
                            try {
                                val messages = ApiService.instance.getDashboardMessages()
                                messages.forEach { msg ->
                                    renderer.processMessage(msg)
                                }
                                isLoading = false
                            } catch (e: Exception) {
                                errorMsg = "Không thể tải: ${e.message}"
                                isLoading = false
                            }
                        }
                    }) {
                        Text("Tải lại")
                    }
                }
            } else {
                val surfaceContext = renderer.getSurfaceContext("dashboard_surface")
                val rootComponent = renderer.getComponent("dashboard_surface", "root")

                if (surfaceContext != null && rootComponent != null) {
                    val registry = remember { ComponentRegistry(renderer) }
                    registry.render(rootComponent, surfaceContext)
                } else {
                    Text("Không tìm thấy giao diện Dashboard", modifier = Modifier.align(Alignment.Center))
                }
            }
        }
    }
}
