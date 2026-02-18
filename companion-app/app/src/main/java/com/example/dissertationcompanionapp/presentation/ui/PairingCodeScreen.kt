package com.example.dissertationcompanionapp.presentation.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import androidx.wear.compose.material.Button
import androidx.wear.compose.material.ButtonDefaults
import androidx.wear.compose.material.Text
import com.example.dissertationcompanionapp.presentation.viewmodels.MainViewModel

@Composable
fun PairingCodeScreen(navController: NavController, viewModel: MainViewModel){
    val address by viewModel.address.collectAsState()

    var text by remember { mutableStateOf("") }

    LaunchedEffect(address) {
        if (!address.isNullOrEmpty()) {
            navController.navigate("hrv_screen") {
                popUpTo("pairing_screen") { inclusive = true }
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(8.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        TextField(
            value = text.uppercase(),
            onValueChange = { newValue ->
                text = newValue.filter { it.isLetterOrDigit() }.take(12)
            },
            label = { Text("Enter pairing code") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Submit button: enabled only when 12 characters are entered
        Button(
            onClick = { viewModel.saveAddress(text) },
            enabled = text.length == 12,
            colors = ButtonDefaults.buttonColors()
        ) {
            Text("Submit")
        }
    }
}