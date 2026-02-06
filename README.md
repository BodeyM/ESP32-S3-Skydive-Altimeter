# CircuitPython Skydive Altimeter

This is a DIY digital visual altimeter powered by the ESP32-S3 and CircuitPython. It utilizes a barometric pressure sensor to track altitude, manage power states, and display critical phase-specific messages (Ascent vs. Descent) to the jumper.

> ⚠️ **DANGER** ⚠️
>
> **DO NOT USE THIS DEVICE AS YOUR PRIMARY ALTIMETER.**
> 
> This software and hardware design is for **educational and hobbyist purposes only**. It has not been tested against industry safety standards. Electronics can fail, batteries can die, and code can crash.
>
> **ALWAYS** jump with a multiple redundant system of industry standard, commercially manufactured audible and visual altimeters.

## 🌟 Features

*   **Smart Zeroing:** Automatically detects ground level by analyzing pressure variance while stationary.
*   **Flight State Detection:** Automatically switches between "Ground Mode" (low power, slow poll) and "Flight Mode" (high refresh rate).
*   **Dynamic Display:**
    *   Below 1,000 ft: Displays precise feet (e.g., `68'`).
    *   Above 1,000 ft: Displays in thousands (e.g., `12.5k`).
*   **Phase-Specific Alerts:**
    *   **Ascent:** "SEATBELT" (1,500'), "CHECK GEAR" (10,000').
    *   **Descent:** "SEPARATE" (5,000'), "PULL" (4,000').
    *   **Safety Latch:** Descent alarms are only armed if the device climbs above 6,000', preventing false alarms during the climb.
*   **Power Management:**
    *   Wi-Fi and Bluetooth are strictly disabled to conserve power.
    *   Integrated Battery Fuel Gauge (LC709203F) display.

## 🛠️ Hardware Requirements

This code is designed for the following hardware stack, though it can be adapted:

*   **Microcontroller:** ESP32-S3 (e.g., Adafruit Feather ESP32-S3).
*   **Sensor:** BMP280 Barometric Pressure Sensor (I2C).
*   **Display:** 1.14" 240x135 Color TFT (ST7789 driver).
*   **Battery Monitor:** LC709203F (Built-in to many Adafruit Feather boards).
*   **Battery:** 3.7V LiPo.

## 📂 File Structure

The project is modularized for maintainability:

```text
CIRCUITPY/
├── lib/                   # CircuitPython Libraries
├── font/                  # Bitmap Fonts
├── code.py                # Main entry point; runs the state machine loop
├── settings.py            # User configuration (Thresholds, Pin definitions)
├── hardware.py            # Hardware initialization (I2C, SPI, Radio disabling)
├── altimeter.py           # Math logic (Zeroing algorithm, Pressure conversion)
└── ui.py                  # Display logic (Text formatting, Graphics updates)
```

## ⚙️ Installation

1.  **Install CircuitPython:** Flash your ESP32-S3 board with the latest version of CircuitPython.
2.  **Install Libraries:** Copy the following libraries from the [CircuitPython Bundle](https://circuitpython.org/libraries) to the `lib` folder on your device:
    *   `adafruit_bmp280`
    *   `adafruit_st7789`
    *   `adafruit_display_text`
    *   `adafruit_lc709203f`
    *   `adafruit_bitmap_font`
3.  **Upload Code:** Copy all `.py` files (`code.py`, `settings.py`, etc.) to the root of the `CIRCUITPY` drive.

## 🔧 Configuration (`settings.py`)

You can adjust altitude thresholds and pin mappings without touching the core logic.

```python
# settings.py

# Altimeter Settings
GROUND_TOLERANCE_FT = 10     # Allowed variance to consider "stable"
TAKEOFF_THRESHOLD = 300      # Feet above ground to enter Flight Mode
LANDING_THRESHOLD = 200      # Feet above ground to enter Ground Mode

# Alert Thresholds (Feet)
ALT_SEATBELT = 1500
ALT_CHECK_GEAR = 10000
ALT_SEPARATE = 5000
ALT_PULL = 4000
```

## 🧠 Logic Overview

### 1. Ground Mode (Idle)
*   **Refresh Rate:** 2.0 seconds.
*   **Zeroing:** The device keeps a history of the last 20 pressure readings. If the variance (Max - Min) is less than `GROUND_TOLERANCE_FT` for 5 seconds, the device re-zeros itself to the current pressure.

### 2. Flight Mode (Active)
*   Triggered when altitude > `TAKEOFF_THRESHOLD` (300').
*   **Refresh Rate:** 0.5 seconds (2 Hz).
*   **Ascent Logic:** Displays "REMOVE SEATBELT" and "CHECK GEAR" messages momentarily as you cross those altitudes.
*   **The "Apogee Latch":** The system sets a flag `has_reached_high_altitude` only after crossing 6,000'. This ensures that descent messages ("PULL") never appear while you are climbing up in the airplane.

### 3. Descent Mode
*   Triggered when altitude drops, provided the **Apogee Latch** is set.
*   **Priority:** If altitude < 4,000', the "PULL" message overrides all other UI elements.

## 🔋 Power Consumption

To maximize battery life for a full day of jumping:
1.  **Radios Off:** The `hardware.py` module explicitly disables `wifi.radio` and `_bleio` (Bluetooth) on boot.
2.  **Variable Polling:** The device sleeps longer between checks when on the ground.

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

The source code of this project is licensed under [MIT](https://choosealicense.com/licenses/mit/).

The fonts 'CrimsonPro-30' and 'CrimsonPro-96' are a derivative of 'Crimson Pro', licensed under the SIL Open Font License, Version 1.1.
