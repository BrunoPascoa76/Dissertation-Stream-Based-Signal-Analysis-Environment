package com.example.dissertationcompanionapp.presentation.viewmodels

import android.util.Log
import androidx.lifecycle.ViewModel
import com.example.dissertationcompanionapp.presentation.data.AddressRepository
import com.example.dissertationcompanionapp.presentation.data.UUIDRepository
import com.example.dissertationcompanionapp.presentation.data.WatchCommand
import com.hivemq.client.mqtt.datatypes.MqttQos
import com.hivemq.client.mqtt.mqtt5.Mqtt5AsyncClient
import com.hivemq.client.mqtt.mqtt5.Mqtt5Client
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.serialization.json.Json
import org.json.JSONObject
import java.util.UUID
import kotlinx.serialization.decodeFromString

class MQTTViewModel(
    private val addressRepository: AddressRepository,
    private val uuidRepository: UUIDRepository
): ViewModel() {
    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected

    private val _sessionStarted = MutableStateFlow(false)
    val sessionStarted: StateFlow<Boolean> = _sessionStarted

    private var mqttClient: Mqtt5AsyncClient? = null

    private val json = Json {
        ignoreUnknownKeys = true
    }

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
            ?.willPublish() //if it goes down unexpectedly, it warns the desktop
            ?.topic("sessions/status/hrv")
            ?.payload("""{"event":"unexpected_disconnect"}""".toByteArray())
            ?.qos(MqttQos.AT_LEAST_ONCE)
            ?.applyWillPublish()
            ?.send()
            ?.whenComplete { _, throwable ->
                if (throwable == null) {
                    _isConnected.value = true
                    subscribeToCommands()
                }
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
        if (message.isNullOrBlank()) return

        try {
            val command = json.decodeFromString<WatchCommand>(message)

            when (command.command.lowercase()) {

                "start" -> {
                    if (!command.uuid.isNullOrBlank()) {
                        uuidRepository.saveUUID(command.uuid)
                        _sessionStarted.value = true
                    } else {
                        // Optional: log invalid start without UUID
                    }
                }

                "stop" -> {
                    _sessionStarted.value = false
                }
            }

        } catch (e: Exception) {
            e.printStackTrace() // optional: replace with Log.e
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

        val uuid = uuidRepository.getUUID() ?: return

        val json = JSONObject().apply {
            put("uuid",uuid)
            put("timestamp", timestamp)
            put("value", hrv)
        }

        mqttClient?.publishWith()
            ?.topic("/sensors/hrv")
            ?.payload(json.toString().toByteArray())
            ?.qos(MqttQos.AT_LEAST_ONCE)
            ?.send()
    }
}