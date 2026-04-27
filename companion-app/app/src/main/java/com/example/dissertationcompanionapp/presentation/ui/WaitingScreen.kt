package com.example.dissertationcompanionapp.presentation.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.dissertationcompanionapp.presentation.viewmodels.MQTTViewModel
import com.example.dissertationcompanionapp.presentation.viewmodels.MainViewModel

@Composable
fun HRVWrapper(viewModel: MainViewModel, mqttViewModel: MQTTViewModel,navController: NavController) {
    val isConnected by mqttViewModel.isConnected.collectAsState()
    val sessionStarted by mqttViewModel.sessionStarted.collectAsState()
    val address by viewModel.address.collectAsState()
    mqttViewModel.connect()

    if(address==null){
        navController.navigate("pairing_screen"){
            popUpTo("hrv_screen") { inclusive = true }
        }
    }

    if (isConnected && sessionStarted) {
        HRVScreen(viewModel,mqttViewModel)
    } else {
        WaitingScreen(isConnected, sessionStarted, onClearAddress = {viewModel.clearAddress()})
    }
}

@Composable
fun WaitingScreen(isConnected: Boolean, sessionStarted: Boolean,onClearAddress:()->Unit) {
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
            textAlign = TextAlign.Center,
            text = when {
                !isConnected -> "Connecting to MQTT..."
                !sessionStarted -> "Waiting for session to start..."
                else -> "Preparing..."
            },
            style = MaterialTheme.typography.bodyLarge
        )
        Button(onClick=onClearAddress){
            Text(text="Clear address")
        }
    }
}