import time
import settings

class AltimeterLogic:
    def __init__(self, sensor):
        self.sensor = sensor
        self.ground_pressure = sensor.pressure
        self.current_altitude = 0.0
        
        # Stability tracking
        self.history = []
        self.last_stable_check = time.monotonic()
        
        # Flags
        self.is_flying = False
        
    def read_raw_altitude(self):
        """Standard pressure conversion formula."""
        pressure = self.sensor.pressure
        # Calculate altitude based on fixed sea level, we will offset this later
        # 44330 * (1.0 - (p / p0) ** 0.1903)
        return 44330 * (1.0 - (pressure / self.ground_pressure) ** 0.1903) * 3.28084

    def update(self):
        """
        Main logic called by the loop.
        Returns: (altitude_feet, is_flying_bool)
        """
        
        # Get current absolute pressure altitude (relative to when we last zeroed)
        # Note: We recalculate based on current ground_pressure setting
        raw_alt = 44330 * (1.0 - (self.sensor.pressure / self.ground_pressure) ** 0.1903) * 3.28084
        self.current_altitude = raw_alt
        
        now = time.monotonic()

        # --- GROUND LOGIC ---
        if not self.is_flying:
            # Add sample to history buffer
            self.history.append(raw_alt)
            # Keep only last N samples (assuming update rate, e.g., 20 samples)
            if len(self.history) > 20: 
                self.history.pop(0)

            # Check stability every few seconds
            if now - self.last_stable_check > settings.GROUND_SAMPLE_WINDOW:
                if self.history:
                    min_h = min(self.history)
                    max_h = max(self.history)
                    variance = max_h - min_h
                    
                    # If variance is low, we are sitting still. Re-zero.
                    if variance < settings.GROUND_TOLERANCE_FT:
                        # Reset ground pressure to current current pressure
                        self.ground_pressure = self.sensor.pressure
                        self.history = [] # Clear history
                        print("Re-Zeroed Ground Level")
                
                self.last_stable_check = now

            # Check for Takeoff
            if raw_alt > settings.TAKEOFF_THRESHOLD:
                self.is_flying = True
                print("Takeoff Detected -> Active Mode")

        # --- FLIGHT LOGIC ---
        else:
            # Check for Landing
            if raw_alt < settings.LANDING_THRESHOLD:
                # We need a debounce here normally, but for simplicity:
                self.is_flying = False
                print("Landing Detected -> Ground Mode")

        return self.current_altitude, self.is_flying