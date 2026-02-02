import time
import settings
import hardware
import ui
import altimeter

# 1. Setup
display, bmp, batt_monitor = hardware.setup_hardware()
screen = ui.AltimeterUI(display)
alti = altimeter.AltimeterLogic(bmp)

# 2. State Alert Flags
# We track specific one-time alerts here
alerts_triggered = {
    "seatbelt": False,
    "check_gear": False
}

# 3. Flight Phase Tracking
# This prevents "PULL" from showing while we are climbing up in the plane.
has_reached_high_altitude = False 
MIN_JUMP_ALTITUDE = 6000 # We must go above this to enable descent messages

def reset_flight_state():
    global has_reached_high_altitude
    has_reached_high_altitude = False
    for key in alerts_triggered:
        alerts_triggered[key] = False

# Battery Timing Variables
last_batt_check = 0
batt_check_interval = 10.0 # Check battery every 10 seconds
current_batt_percent = 0

# 4. Main Loop
last_update = 0

while True:
    now = time.monotonic()
    
    # Determine Refresh Rate based on mode
    # Active flight = fast refresh (0.5s), Ground = slow refresh (2.0s)
    if alti.is_flying:
        refresh_interval = 0.5 
    else:
        refresh_interval = 2.0 
        
    if now - last_update >= refresh_interval:
        last_update = now
        
        # Get Data
        alt_ft, is_flying = alti.update()

        # --- NEW: Battery Logic ---
        # We check this less frequently than the altitude
        if batt_monitor and (now - last_batt_check > batt_check_interval):
            try:
                current_batt_percent = batt_monitor.cell_percent
            except OSError:
                current_batt_percent = 0 # Handle I2C read error
            last_batt_check = now
        
        # --- Message Logic ---
        current_message = ""
        
        if not is_flying:
            # We are on the ground
            reset_flight_state()
            current_message = "GROUND"
        else:
            # We are in the air
            
            # --- 1. ASCENT CHECK ---
            # Check if we have crossed the threshold to enable descent messages later
            if alt_ft > MIN_JUMP_ALTITUDE:
                has_reached_high_altitude = True

            # --- 2. ASCENT ALERTS ---
            
            # Message: Remove Seatbelt (> 1500')
            # Logic: Show if we are above 1500, haven't shown it yet, and aren't super high yet
            if alt_ft > settings.ALT_SEATBELT and not alerts_triggered["seatbelt"]:
                # Only show this during the climb phase (before we get too high)
                if alt_ft < settings.ALT_SEATBELT + 1000: 
                    current_message = "SEATBELT"
                else:
                    # We missed the window or showed it long enough, mark done
                    alerts_triggered["seatbelt"] = True

            # Message: Check Gear (> 10000')
            if alt_ft > settings.ALT_CHECK_GEAR and not alerts_triggered["check_gear"]:
                if alt_ft < settings.ALT_CHECK_GEAR + 1000:
                    current_message = "CHECK GEAR"
                else:
                    alerts_triggered["check_gear"] = True

            # --- 3. DESCENT ALERTS ---
            # These only trigger if we have previously gone high (has_reached_high_altitude)
            
            if has_reached_high_altitude:
                
                # Message: Separate (< 5000')
                # We check if we are below 5000 BUT above the Pull altitude
                if settings.ALT_PULL < alt_ft < settings.ALT_SEPARATE:
                    current_message = "SEPARATE"
            
                # Message: PULL (< 4000')
                # We check if we are below 4000 but above a landing buffer (e.g. 1000)
                # so it doesn't say PULL while you are landing under canopy.
                elif 2000 < alt_ft < settings.ALT_PULL:
                    current_message = "PULL"
                
        # Update Screen (Pass the battery percent now)
        screen.update(alt_ft, current_message, current_batt_percent)