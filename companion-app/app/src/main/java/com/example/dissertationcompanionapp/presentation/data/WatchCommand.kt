package com.example.dissertationcompanionapp.presentation.data

import kotlinx.serialization.Serializable

@Serializable
data class WatchCommand(
    val command: String,
    val uuid: String? = null
)
