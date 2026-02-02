import board

# Hardware Pins (Adjust to your specific wiring)
PIN_SPI = board.SPI()
PIN_TFT_CS = board.TFT_CS
PIN_TFT_DC = board.TFT_DC

# Altimeter Settings
GROUND_TOLERANCE_FT = 10     # Plus/minus variance allowed for "stable" reading
GROUND_SAMPLE_WINDOW = 5.0   # Seconds to hold steady before re-zeroing
TAKEOFF_THRESHOLD = 100      # Feet above ground to trigger "Flight Mode"
LANDING_THRESHOLD = 200      # Feet above ground to return to "Ground Mode"

# Alert Thresholds (in Feet)
ALT_SEATBELT = 1500
ALT_CHECK_GEAR = 10000
ALT_SEPARATE = 5000
ALT_PULL = 4000