package com.example.dissertationcompanionapp.presentation.viewmodels

import android.app.Application
import android.content.Context
import androidx.lifecycle.ViewModel
import com.example.dissertationcompanionapp.presentation.data.AddressRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import org.eclipse.paho.client.mqttv3.IMqttActionListener
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken
import org.eclipse.paho.client.mqttv3.IMqttToken
import org.eclipse.paho.client.mqttv3.MqttCallback
import org.eclipse.paho.client.mqttv3.MqttClient
import org.eclipse.paho.client.mqttv3.MqttConnectOptions
import org.eclipse.paho.client.mqttv3.MqttMessage
import org.json.JSONObject

class MQTTViewModel(
    private val application: Application,
    private val addressRepository: AddressRepository
): ViewModel() {
    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected

    private val _sessionStarted = MutableStateFlow(false)
    val sessionStarted: StateFlow<Boolean> = _sessionStarted

    private var mqttClient: MqttAndroidClient? = null

    fun connect() {
        val address = addressRepository.getAddress()
        val serverUri = "tcp://$address"

        val clientId = MqttClient.generateClientId()

        mqttClient = MqttAndroidClient(
            application.applicationContext,
            serverUri,
            clientId
        )

        val options = MqttConnectOptions().apply {
            isAutomaticReconnect = true
            isCleanSession = false
        }

        mqttClient?.setCallback(object : MqttCallback {

            override fun connectionLost(cause: Throwable?) {
                _isConnected.value = false
            }

            override fun messageArrived(topic: String?, message: MqttMessage?) {
                if (topic == "commands/hrv") {
                    handleCommand(message?.toString())
                }
            }

            override fun deliveryComplete(token: IMqttDeliveryToken?) {}
        })

        mqttClient?.connect(options, null, object : IMqttActionListener {

            override fun onSuccess(asyncActionToken: IMqttToken?) {
                _isConnected.value = true
                mqttClient?.subscribe("commands/hrv", 1)
            }

            override fun onFailure(
                asyncActionToken: IMqttToken?,
                exception: Throwable?
            ) {
                _isConnected.value = false
            }
        })
    }

    private fun handleCommand(message: String?) {
        when (message?.lowercase()) {
            "start" -> _sessionStarted.value = true
            "stop" -> _sessionStarted.value = false
        }
    }

    fun disconnect() {
        mqttClient?.disconnect()
        _isConnected.value = false
        _sessionStarted.value = false
    }

    override fun onCleared() {
        super.onCleared()
        disconnect()
    }

    fun publishHrvData(hrv: Double, timestamp:Long){
        if (!_isConnected.value || !_sessionStarted.value) return

        val json = JSONObject().apply {
            put("timestamp", timestamp)
            put("hrv", hrv)
        }

        val message = MqttMessage(json.toString().toByteArray()).apply {
            qos = 1
        }

        mqttClient?.publish("/sensors/hrv", message)
    }
}