import displayio
import terminalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

class AltimeterUI:
    def __init__(self, display):
        self.display = display
        self.main_group = displayio.Group()

        altFont = bitmap_font.load_font("font/CrimsonPro-96.bdf")
        messageFont = bitmap_font.load_font("font/CrimsonPro-30.bdf")
        
        # Main Altitude Text
        self.lbl_alt = label.Label(
            altFont, 
            text="INIT", 
            color=0xFFFFFF, 
            anchor_point=(0.5, 1.0),
            anchored_position=(120, 110)
        )
        
        # Message Text (Red alert text)
        self.lbl_msg = label.Label(
            messageFont,
            text="",
            color=0xFF0000,
            anchor_point=(0.5, 0),
            anchored_position=(120, 10)
        )

        # NEW: Battery Text (Small, Top Right)
        self.lbl_batt = label.Label(
            terminalio.FONT,
            text="--%",
            color=0x00FF00, # Green text
            scale=1,        # Small text
            anchor_point=(1.0, 0), # Anchor to top-right
            anchored_position=(display.width - 5, 5)
        )

        self.main_group.append(self.lbl_alt)
        self.main_group.append(self.lbl_msg)
        self.main_group.append(self.lbl_batt) # Add to group
        self.display.root_group = self.main_group

    def format_altitude(self, feet):
        """Formats altitude according to specifications."""
        if feet < 1000:
            return f"{int(feet)}'"
        else:
            k_val = feet / 1000.0
            return f"{k_val:.1f}k"

    def update(self, altitude_ft, message=None, batt_percent=None):
        # Update Altitude
        new_text = self.format_altitude(altitude_ft)
        if self.lbl_alt.text != new_text:
            self.lbl_alt.text = new_text
            
        # Update Message
        msg_text = message if message else ""
        if self.lbl_msg.text != msg_text:
            self.lbl_msg.text = msg_text

        # NEW: Update Battery
        # Only update if a value is passed (we might not check battery every loop)
        if batt_percent is not None:
            batt_text = f"{int(batt_percent)}%"
            if self.lbl_batt.text != batt_text:
                self.lbl_batt.text = batt_text
                
                # Optional: Change color if low battery
                if batt_percent < 20:
                    self.lbl_batt.color = 0xFF0000 # Red
                else:
                    self.lbl_batt.color = 0x00FF00 # Green