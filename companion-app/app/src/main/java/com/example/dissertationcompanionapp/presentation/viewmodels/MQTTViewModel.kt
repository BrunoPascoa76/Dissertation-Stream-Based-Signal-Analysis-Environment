package com.example.dissertationcompanionapp.presentation.viewmodels

import android.util.Log
import androidx.lifecycle.ViewModel
import com.example.dissertationcompanionapp.presentation.data.AddressRepository
import com.hivemq.client.mqtt.mqtt5.Mqtt5AsyncClient
import com.hivemq.client.mqtt.mqtt5.Mqtt5Client
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import org.json.JSONObject
import java.util.UUID

class MQTTViewModel(
    private val addressRepository: AddressRepository
): ViewModel() {
    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected

    private val _sessionStarted = MutableStateFlow(false)
    val sessionStarted: StateFlow<Boolean> = _sessionStarted

    private var mqttClient: Mqtt5AsyncClient? = null

    fun connect() {
        val address = addressRepository.getAddress()

        // HiveMQ handles the 'tcp://' part internally, just provide host and port
        // Assuming address is "IP:PORT" or just "IP"
        val parts = address?.split(":")
        val host = parts?.get(0) ?: "localhost" //not needed, just because it forces me to
        val port = parts?.getOrNull(1)?.toInt() ?: 1883


        mqttClient = Mqtt5Client.builder()
            .identifier(UUID.randomUUID().toString())
            .serverHost(host)
            .serverPort(port)
            .automaticReconnectWithDefaultConfig()
            .buildAsync()

        mqttClient?.connectWith()
            ?.cleanStart(false)
            ?.send()
            ?.whenComplete { _, throwable ->
                if (throwable == null) {
                    _isConnected.value = true
                    // We subscribe immediately after connecting
                    subscribeToCommands()
                }
        }
    }

    private fun subscribeToCommands() {
        mqttClient?.subscribeWith()
            ?.topicFilter("commands/hrv")
            ?.callback { publish ->
                val message = publish.payloadAsBytes.decodeToString()
                handleCommand(message)
            }
            ?.send()
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

    fun publishHrvData(hrv: Double, timestamp: Long) {
        if (!_isConnected.value || !_sessionStarted.value) return

        val json = JSONObject().apply {
            put("timestamp", timestamp)
            put("hrv", hrv)
        }

        mqttClient?.publishWith()
            ?.topic("/sensors/hrv")
            ?.payload(json.toString().toByteArray())
            ?.qos(com.hivemq.client.mqtt.datatypes.MqttQos.AT_LEAST_ONCE)
            ?.send()
    }
}