package com.example.dissertationcompanionapp.presentation

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.ContextCompat
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.dissertationcompanionapp.presentation.data.AddressRepository
import com.example.dissertationcompanionapp.presentation.data.UUIDRepository
import com.example.dissertationcompanionapp.presentation.theme.DissertationCompanionAppTheme
import com.example.dissertationcompanionapp.presentation.ui.HRVWrapper
import com.example.dissertationcompanionapp.presentation.ui.PairingCodeScreen
import com.example.dissertationcompanionapp.presentation.viewmodels.MQTTViewModel
import com.example.dissertationcompanionapp.presentation.viewmodels.MainViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val requestPermissionLauncher = registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { isGranted: Boolean ->
            if (!isGranted) {
                finish()
            }
        }

        // Check and request
        when {
            ContextCompat.checkSelfPermission(
                this, Manifest.permission.BODY_SENSORS
            ) == PackageManager.PERMISSION_GRANTED -> {
                // Already have it, carry on
            }
            else -> {
                requestPermissionLauncher.launch(Manifest.permission.BODY_SENSORS)
            }
        }

        setContent {
            DissertationCompanionAppTheme {
                MainApp()
            }
        }
    }
}

@Composable
fun MainApp() {
    val navController = rememberNavController()
    val context = LocalContext.current

    val addressRepository = AddressRepository(context)
    val uuidRepository= UUIDRepository(context)
    val mainViewModel = remember {
        MainViewModel(context, addressRepository)
    }
    val mqttViewModel = remember {
        MQTTViewModel(addressRepository, uuidRepository)
    }

    WearAppNav(navController, mainViewModel, mqttViewModel)
}

@Composable
fun WearAppNav(navController: NavHostController, viewModel: MainViewModel, mqttViewModel: MQTTViewModel) {
    NavHost(navController, startDestination = "pairing_screen") {
        composable("pairing_screen") {
            PairingCodeScreen(navController, viewModel)
        }
        composable("hrv_screen") {
            HRVWrapper(viewModel, mqttViewModel)
        }
    }
}