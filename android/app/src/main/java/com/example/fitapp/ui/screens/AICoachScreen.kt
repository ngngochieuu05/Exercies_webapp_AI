package com.example.fitapp.ui.screens

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.example.fitapp.data.network.ApiService
import com.example.fitapp.data.network.ChatRequest
import kotlinx.coroutines.launch
import org.a2ui.compose.rendering.*

data class Message(
    val sender: String, // "user" or "ai"
    val text: String,
    val a2uiMessages: List<String>? = null
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AICoachScreen() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    var textInput by remember { mutableStateOf("") }
    val messages = remember { mutableStateListOf<Message>() }
    var isSending by remember { mutableStateOf(false) }

    // Start with a welcome message
    LaunchedEffect(Unit) {
        if (messages.isEmpty()) {
            messages.add(
                Message(
                    sender = "ai",
                    text = "Chào bạn! Tôi là trợ lý AI Coach. Hãy hỏi tôi về các bài tập hoặc nói 'đề xuất bài tập' nhé!"
                )
            )
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Trợ lý AI Coach") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.background)
                .padding(innerPadding)
        ) {
            // Chat list
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                items(messages) { message ->
                    ChatBubble(message)
                }
            }

            // Input row
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.surface)
                    .navigationBarsPadding()
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextField(
                    value = textInput,
                    onValueChange = { textInput = it },
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(24.dp)),
                    placeholder = { Text("Nhập tin nhắn...") },
                    enabled = !isSending,
                    colors = TextFieldDefaults.colors(
                        focusedContainerColor = MaterialTheme.colorScheme.surfaceVariant,
                        unfocusedContainerColor = MaterialTheme.colorScheme.surfaceVariant,
                        disabledContainerColor = MaterialTheme.colorScheme.surfaceVariant,
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent
                    ),
                    singleLine = true
                )
                Spacer(modifier = Modifier.width(8.dp))
                Button(
                    onClick = {
                        if (textInput.isBlank()) return@Button
                        val userMsg = textInput
                        textInput = ""
                        messages.add(Message("user", userMsg))
                        isSending = true
                        
                        coroutineScope.launch {
                            try {
                                val response = ApiService.instance.sendChatMessage(ChatRequest(userMsg))
                                messages.add(
                                    Message(
                                        sender = "ai",
                                        text = response.reply,
                                        a2uiMessages = response.a2ui_messages
                                    )
                                )
                            } catch (e: Exception) {
                                messages.add(
                                    Message(
                                        sender = "ai",
                                        text = "Xin lỗi, đã xảy ra lỗi kết nối: ${e.message}"
                                    )
                                )
                            } finally {
                                isSending = false
                            }
                        }
                    },
                    enabled = !isSending && textInput.isNotBlank(),
                    shape = RoundedCornerShape(24.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary,
                        contentColor = MaterialTheme.colorScheme.onPrimary
                    )
                ) {
                    if (isSending) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(18.dp),
                            color = MaterialTheme.colorScheme.onPrimary,
                            strokeWidth = 2.dp
                        )
                    } else {
                        Text("Gửi")
                    }
                }
            }
        }
    }
}

@Composable
fun ChatBubble(message: Message) {
    val isUser = message.sender == "user"
    val context = LocalContext.current
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = if (isUser) Alignment.End else Alignment.Start
    ) {
        // Chat text
        Box(
            modifier = Modifier
                .background(
                    color = if (isUser) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant,
                    shape = RoundedCornerShape(
                        topStart = 16.dp,
                        topEnd = 16.dp,
                        bottomStart = if (isUser) 16.dp else 0.dp,
                        bottomEnd = if (isUser) 0.dp else 16.dp
                    )
                )
                .padding(12.dp)
                .widthIn(max = 280.dp)
        ) {
            Text(
                text = message.text,
                color = if (isUser) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        // Render inline A2UI surface if present
        if (!isUser && message.a2uiMessages != null) {
            Spacer(modifier = Modifier.height(8.dp))
            val renderer = remember { A2UIRenderer() }
            
            val actionHandler = remember {
                object : ActionHandler {
                    override fun onAction(surfaceId: String, actionName: String, actionContext: Map<String, Any>) {
                        Toast.makeText(context, "AI Coach ghi nhận hoàn thành bài tập!", Toast.LENGTH_LONG).show()
                    }
                    override fun openUrl(url: String) {}
                    override fun showToast(message: String) {
                        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
                    }
                }
            }
            
            LaunchedEffect(message.a2uiMessages) {
                renderer.setActionHandler(actionHandler)
                try {
                    message.a2uiMessages.forEach { msg ->
                        renderer.processMessage(msg)
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }

            Box(
                modifier = Modifier
                    .widthIn(max = 300.dp)
                    .background(MaterialTheme.colorScheme.surfaceVariant, shape = RoundedCornerShape(12.dp))
                    .padding(8.dp)
            ) {
                val surfaceContext = renderer.getSurfaceContext("chat_surface")
                val rootComponent = renderer.getComponent("chat_surface", "root")

                if (surfaceContext != null && rootComponent != null) {
                    val registry = remember { ComponentRegistry(renderer) }
                    registry.render(rootComponent, surfaceContext)
                } else {
                    CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                }
            }
        }
    }
}

