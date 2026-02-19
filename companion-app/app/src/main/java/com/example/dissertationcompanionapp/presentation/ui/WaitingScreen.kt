package com.example.dissertationcompanionapp.presentation.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.dissertationcompanionapp.presentation.viewmodels.MQTTViewModel
import com.example.dissertationcompanionapp.presentation.viewmodels.MainViewModel

@Composable
fun HRVWrapper(viewModel: MainViewModel, mqttViewModel: MQTTViewModel) {
    val isConnected by mqttViewModel.isConnected.collectAsState()
    val sessionStarted by mqttViewModel.sessionStarted.collectAsState()
    mqttViewModel.connect()

    if (isConnected && sessionStarted) {
        HRVScreen(viewModel,mqttViewModel)
    } else {
        WaitingScreen(isConnected, sessionStarted)
    }
}

@Composable
fun WaitingScreen(isConnected: Boolean, sessionStarted: Boolean) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        CircularProgressIndicator()
        Spacer(modifier = Modifier.padding(16.dp))
        Text(
            text = when {
                !isConnected -> "Connecting to MQTT..."
                !sessionStarted -> "Waiting for session to start..."
                else -> "Preparing..."
            },
            style = MaterialTheme.typography.bodyLarge
        )
    }
}