package com.example.dissertationcompanionapp.presentation

import android.Manifest
import android.app.Application
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.wear.compose.foundation.lazy.TransformingLazyColumn
import androidx.wear.compose.foundation.lazy.rememberTransformingLazyColumnState
import androidx.wear.compose.material3.AppScaffold
import androidx.wear.compose.material3.Button
import androidx.wear.compose.material3.ButtonDefaults
import androidx.wear.compose.material3.EdgeButton
import androidx.wear.compose.material3.ListHeader
import androidx.wear.compose.material3.MaterialTheme
import androidx.wear.compose.material3.ScreenScaffold
import androidx.wear.compose.material3.SurfaceTransformation
import androidx.wear.compose.material3.Text
import androidx.wear.compose.material3.lazy.rememberTransformationSpec
import androidx.wear.compose.material3.lazy.transformedHeight
import androidx.wear.compose.ui.tooling.preview.WearPreviewDevices
import androidx.wear.compose.ui.tooling.preview.WearPreviewFontScales
import com.example.dissertationcompanionapp.R
import com.example.dissertationcompanionapp.presentation.data.AddressRepository
import com.example.dissertationcompanionapp.presentation.theme.DissertationCompanionAppTheme
import com.example.dissertationcompanionapp.presentation.ui.HRVScreen
import com.example.dissertationcompanionapp.presentation.ui.HRVWrapper
import com.example.dissertationcompanionapp.presentation.ui.PairingCodeScreen
import com.example.dissertationcompanionapp.presentation.viewmodels.MQTTViewModel
import com.example.dissertationcompanionapp.presentation.viewmodels.MainViewModel
import com.example.dissertationcompanionapp.presentation.viewmodels.decodePairingCode

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
    val mainViewModel = remember {
        MainViewModel(context, addressRepository)
    }
    val mqttViewModel = remember {
        MQTTViewModel(addressRepository)
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