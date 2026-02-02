import board
import fourwire
import displayio
import terminalio
import wifi
import _bleio
from adafruit_st7789 import ST7789
from adafruit_lc709203f import LC709203F, PackSize
import adafruit_bmp280
import settings

def setup_hardware():

    # --- POWER SAVING ---
    # Disable Wi-Fi
    wifi.radio.enabled = False
    
    # Disable Bluetooth
    _bleio.adapter.enabled = False

    # Setup Display Bus
    displayio.release_displays()
    spi = board.SPI()
    display_bus = fourwire.FourWire(spi, command=settings.PIN_TFT_DC, chip_select=settings.PIN_TFT_CS)
    
    display = ST7789(display_bus, rotation=270, width=240, height=135, rowstart=40, colstart=53)

    # Setup I2C
    i2c = board.I2C()

    # Setup pressure sensor
    bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
    
    # Set sea level pressure to standard initially (will be zeroed out anyway)
    bmp.sea_level_pressure = 1013.25
    
    #  Setup Battery Monitor
    battery_monitor = None
    try:
        battery_monitor = LC709203F(i2c)
        battery_monitor.pack_size = PackSize.MAH1000 
    except Exception as e:
        print("Battery monitor not found:", e)
    
    return display, bmp, battery_monitor