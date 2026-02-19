package com.example.dissertationcompanionapp.presentation.viewmodels

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.lifecycle.ViewModel
import com.example.dissertationcompanionapp.presentation.data.AddressRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.math.BigInteger
import java.net.InetAddress

class MainViewModel(
    private val context: Context,
    private val addressRepository: AddressRepository
): ViewModel(), SensorEventListener {

    private val _address = MutableStateFlow<String?>(null)
    val address: StateFlow<String?> = _address

    private val _bpm = MutableStateFlow(0f)
    val bpm: StateFlow<Float> = _bpm

    private val _hrv = MutableStateFlow<Double?>(null)
    val hrv: StateFlow<Double?> = _hrv

    var lastBpm: Float = 0f
    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val heartRateSensor: Sensor? = sensorManager.getDefaultSensor(Sensor.TYPE_HEART_RATE)

    init {
        _address.value = addressRepository.getAddress()
        startHeartRateSensor()
    }

    fun startHeartRateSensor() {
        heartRateSensor?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_UI)
        }
    }

    override fun onSensorChanged(event: SensorEvent) {
        if (event.sensor.type == Sensor.TYPE_HEART_RATE) {
            val bpmValue = event.values[0]
            if (bpmValue > 0) {
                _bpm.value = bpmValue
                _hrv.value = estimateRMSSDFromBpm(bpmValue.toInt())
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    //Approximate RMSSD from BPM using 3% of RR interval
    private fun estimateRMSSDFromBpm(bpm: Int): Double {
        val rr = 60000.0 / bpm
        return rr * 0.03
    }

    fun saveAddress(encoded: String) {
        val unpacked = decodePairingCode(encoded)
        if (unpacked != null) {
            val (ip, port, _) = unpacked
            val fullAddress = "$ip:$port"
            addressRepository.saveAddress(fullAddress)
            _address.value = fullAddress
        } else {
            // Invalid code entered
            _address.value = null
        }
    }

    override fun onCleared() {
        super.onCleared()
        sensorManager.unregisterListener(this)
    }
}

fun decodePairingCode(code: String): Triple<String?, Int, Int>? {
    val alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ" //probably there's a better way than this, but this is how I could do it

    // Clean and remove the Checksum (the very last character)
    val cleaned = code.replace("-", "").uppercase()
    if (cleaned.isEmpty()) return null



    try {
        // Convert Base-32 String -> BigInteger
        var value = BigInteger.ZERO
        for (char in cleaned) {
            val digit = alphabet.indexOf(char)
            if (digit == -1) continue // Skip invalid
            value = value.multiply(BigInteger.valueOf(32)).add(BigInteger.valueOf(digit.toLong()))
        }

        // Convert BigInteger back to 7 Bytes
        val rawBytes = value.toByteArray()
        val data = ByteArray(7)

        // Copy the last 7 bytes (ignoring the 0x00 sign byte if present)
        val bytesToCopy = minOf(7, rawBytes.size)
        System.arraycopy(
            rawBytes, rawBytes.size - bytesToCopy,
            data, 7 - bytesToCopy,
            bytesToCopy
        )

        // 4. Unpack
        val ipBytes = data.sliceArray(0..3)
        val port = ((data[4].toInt() and 0xFF) shl 8) or (data[5].toInt() and 0xFF)
        val version = data[6].toInt() and 0xFF
        val ipString = InetAddress.getByAddress(ipBytes).hostAddress

        return Triple(ipString, port, version)
    } catch (e: Exception) {
        return null
    }
}