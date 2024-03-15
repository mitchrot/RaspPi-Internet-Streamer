import RPi.GPIO as GPIO
import time
import os
import smbus

# Define GPIO pins
CLOCK_PIN = 27  # Pin connected to the clock signal of the rotary encoder
DATA_PIN = 22   # Pin connected to the data signal of the rotary encoder
LCD_POWER_PIN = 4  # GPIO pin connected to LCD power control

# Define radio stations with their names and URLs
STATIONS = [
    {"name": "Classic 102.7FM", "url": "https://edge.iono.fm/xice/49_medium.mp3"},
    {"name": "Klassik BR", "url": "https://dispatcher.rndfnk.com/br/brklassik/live/aac/low"},
    {"name": "Schlager BR", "url": "https://dispatcher.rndfnk.com/br/brschlager/live/aac/low"},
    {"name": "Radio Swiss Jazz", "url": "https://stream.srg-ssr.ch/m/rsj/mp3_128"},
    {"name": "NDR Schlager", "url": "https://d131.rndfnk.com/ard/ndr/ndrschlager/live/mp3/128/stream.mp3?aggregator=radio-de&cid=01FHT2AV8CV0BJ9C2Y36JE8P0E&sid=2ddsFbJR3Fbg1x8F369JCaVFAAF&token=4hSw79uqi7xTPvOUa1z7QiOPNoaL3EQsVlcTXOf53AM&tvf=O07zMit1vBdkMTMxLnJuZGZuay5jb20"}
]

# LCD configuration
LCD_WIDTH = 16  # Maximum characters per line
LCD_LINE_1 = 0x80  # LCD RAM address for the first line
LCD_LINE_2 = 0xC0  # LCD RAM address for the second line

# Global variables
current_station_index = 0
player_pid = None

# Initialize I2C bus for LCD
bus = smbus.SMBus(1)
LCD_ADDR = 0x27  # I2C address of the LCD

# LCD functions
def lcd_init():
    """Initialize the LCD display."""
    # Initialize display
    lcd_byte(0x33, LCD_CMD)  # Initialize
    lcd_byte(0x32, LCD_CMD)  # Set to 4-bit mode
    lcd_byte(0x06, LCD_CMD)  # Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # Turn on display
    lcd_byte(0x28, LCD_CMD)  # 2 line display
    lcd_byte(0x01, LCD_CMD)  # Clear display
    time.sleep(0.0005)  # Delay to allow commands to process

def lcd_byte(bits, mode):
    """Send a byte to the LCD."""
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # Send high bits
    bus.write_byte(LCD_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Send low bits
    bus.write_byte(LCD_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    """Toggle enable signal of the LCD."""
    # Toggle enable
    time.sleep(0.0005)  # Delay to stabilize enable
    bus.write_byte(LCD_ADDR, (bits | ENABLE))
    time.sleep(0.0005)  # Delay to stabilize enable
    bus.write_byte(LCD_ADDR, (bits & ~ENABLE))
    time.sleep(0.0005)  # Delay to stabilize enable

def lcd_string(message, line):
    """Display a string on the LCD."""
    print("Displaying message on LCD:", message)
    # Send string to display
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

def update_lcd(message):
    """Update the LCD with a new message."""
    print("Updating LCD with message:", message)
    lcd_string(message, LCD_LINE_1)


# LCD mode and flags
LCD_CHR = 1  # LCD command
LCD_CMD = 0  # LCD data
LCD_BACKLIGHT = 0x08  # On
ENABLE = 0b00000100  # Enable bit

# Initialize encoder
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLOCK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DATA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize global variables for rotary encoder
current_state = GPIO.input(DATA_PIN)
previous_state = current_state

# Define a callback function for rotary encoder
def rotary_callback(channel):
    """Callback function for rotary encoder."""
    global current_station_index, previous_state

    # Read the current state of the encoder
    current_state = GPIO.input(DATA_PIN)

    # Edge detection for debouncing
    if current_state != previous_state:
        if GPIO.input(CLOCK_PIN) == current_state:  # Clockwise rotation
            current_station_index = (current_station_index + 1) % len(STATIONS)
            print(f"Switched to station: {STATIONS[current_station_index]['name']} (Clockwise)")
        else:  # Counter-clockwise rotation
            current_station_index = (current_station_index - 1) % len(STATIONS)
            print(f"Switched to station: {STATIONS[current_station_index]['name']} (Counter-clockwise)")

        # Start the new station
        start_station(current_station_index)

    # Update the previous state
    previous_state = current_state

# Register callback for rotary encoder with edge detection
GPIO.add_event_detect(CLOCK_PIN, GPIO.BOTH, callback=rotary_callback, bouncetime=50)

# Function to start playing a radio station
def start_station(station_index):
    """Start playing the selected radio station."""
    global player_pid
    try:
        # Stop the previous station
        stop_player()

        # Start the new station
        player_pid = os.spawnlp(os.P_NOWAIT, '/usr/local/bin/vlc-wrapper.sh', '/usr/local/bin/vlc-wrapper.sh', STATIONS[station_index]["url"])
        print(f"Now playing: {STATIONS[station_index]['name']}")
        update_lcd(STATIONS[station_index]['name'])  # Display the station name
    except OSError as e:
        print(f"Error launching cvlc: {e}")

# Function to stop the player
def stop_player():
    """Stop the currently playing radio station."""
    global player_pid
    if player_pid:
        os.system(f"kill {player_pid}")
        player_pid = None

try:
    # Set up GPIO pins for LCD power
    GPIO.setup(LCD_POWER_PIN, GPIO.OUT)  # Set LCD power pin as output
    GPIO.output(LCD_POWER_PIN, GPIO.HIGH)  # Initialize LCD power

    # Initialize LCD
    lcd_init()

    # Start the initial station
    start_station(current_station_index)

    # Main loop (no busy waiting)
    while True:
        time.sleep(1)  # Keep the script running

except KeyboardInterrupt:
    GPIO.cleanup()
    stop_player()  # Stop VLC on exit
