package com.example.dissertationcompanionapp.presentation.ui

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.dissertationcompanionapp.presentation.viewmodels.MainViewModel
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MonitorHeart
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.res.painterResource
import com.example.dissertationcompanionapp.R
import com.example.dissertationcompanionapp.presentation.viewmodels.MQTTViewModel

@Composable
fun HRVScreen(viewModel: MainViewModel,mqttViewModel: MQTTViewModel) {
    val hrv by viewModel.hrv.collectAsState()
    val bpm by viewModel.bpm.collectAsState()


    //publish hrv when it changes
    LaunchedEffect(hrv) {
        hrv?.let { value ->
            val timestamp = System.currentTimeMillis()
            mqttViewModel.publishHrvData(value, timestamp)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(8.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        if(bpm>0) {
            BeatingHeart(bpm = bpm)

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                Card(
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier
                        .weight(1f)
                        .padding(4.dp)
                        .background(MaterialTheme.colorScheme.primaryContainer)
                ) {
                    Column(
                        modifier = Modifier.padding(8.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text("BPM", style = MaterialTheme.typography.titleMedium)
                        Text("${bpm.toInt()}", style = MaterialTheme.typography.bodyLarge)
                    }
                }

                Card(
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier
                        .weight(1f)
                        .padding(4.dp)
                        .background(MaterialTheme.colorScheme.secondaryContainer)
                ) {
                    Column(
                        modifier = Modifier.padding(8.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text("HRV", style = MaterialTheme.typography.titleMedium)
                        Text(
                            hrv?.let { String.format("%.1f", it) } ?: "--",
                            style = MaterialTheme.typography.bodyLarge
                        )
                    }
                }
            }
        }else{
            CircularProgressIndicator()
        }

        if(bpm>0){
            Text("Sending values...",style= MaterialTheme.typography.bodyLarge)
        }else{
            Text("Preparing sensors...",style=MaterialTheme.typography.bodyLarge)
        }
    }
}

//just a little flair: the heart beats in sync with bpm (not needed but neat)
@Composable
fun BeatingHeart(
    bpm: Float,
    modifier: Modifier = Modifier
) {
    val safeBpm = if (bpm <= 0f) 60f else bpm
    val beatDuration = (60000f / safeBpm).toInt()

    val infiniteTransition = rememberInfiniteTransition(label = "heartbeat")

    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.25f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = beatDuration / 2,
                easing = FastOutSlowInEasing
            ),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scaleAnim"
    )

    Icon(
        painter = painterResource(R.drawable.ecg_heart_24px),
        contentDescription = null,
        tint=Color.Red,
        modifier = modifier
            .size(60.dp)
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
            }
    )
}