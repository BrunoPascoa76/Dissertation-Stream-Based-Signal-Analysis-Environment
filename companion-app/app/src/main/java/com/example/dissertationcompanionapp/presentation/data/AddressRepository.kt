package com.example.dissertationcompanionapp.presentation.data

import android.content.Context
import androidx.core.content.edit

class AddressRepository(context: Context) {
    private val prefs = context.getSharedPreferences("wearos_companion_app", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_ADDRESS = "mqtt_address"
    }

    fun getAddress(): String? {
        return prefs.getString(KEY_ADDRESS, null)
    }

    fun saveAddress(address: String) {
        prefs.edit { putString(KEY_ADDRESS, address) }
    }

    fun clearAddress() {
        prefs.edit { remove(KEY_ADDRESS) }
    }
}
