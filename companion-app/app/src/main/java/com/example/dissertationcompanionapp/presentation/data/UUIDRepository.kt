package com.example.dissertationcompanionapp.presentation.data

import android.content.Context
import androidx.core.content.edit

class UUIDRepository(context: Context)  {
    private val prefs = context.getSharedPreferences("wearos_companion_app", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_UUID = "uuid"
    }

    fun getUUID(): String? {
        return prefs.getString(KEY_UUID, null)
    }

    fun saveUUID(address: String) {
        prefs.edit { putString(KEY_UUID, address) }
    }

    fun clearUUID() {
        prefs.edit { remove(KEY_UUID) }
    }

}