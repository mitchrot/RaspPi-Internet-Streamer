import RPi.GPIO as GPIO
import time
import os
import smbus
import subprocess

# Define GPIO pins
CLOCK_PIN = 27
DATA_PIN = 22
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
player_process = None

# Initialize I2C bus
bus = smbus.SMBus(1)
LCD_ADDR = 0x27  # I2C address of the LCD

# LCD functions
def lcd_init():
    # Initialize display
    lcd_byte(0x33, LCD_CMD)  # Initialize
    lcd_byte(0x32, LCD_CMD)  # Set to 4-bit mode
    lcd_byte(0x06, LCD_CMD)  # Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # Turn on display
    lcd_byte(0x28, LCD_CMD)  # 2 line display
    lcd_byte(0x01, LCD_CMD)  # Clear display
    time.sleep(0.0005)  # Delay to allow commands to process

def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # Send high bits
    bus.write_byte(LCD_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Send low bits
    bus.write_byte(LCD_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(0.0005)  # Delay to stabilize enable
    bus.write_byte(LCD_ADDR, (bits | ENABLE))
    time.sleep(0.0005)  # Delay to stabilize enable
    bus.write_byte(LCD_ADDR, (bits & ~ENABLE))
    time.sleep(0.0005)  # Delay to stabilize enable

def lcd_string(message, line):
    print("Displaying message on LCD:", message)
    # Send string to display
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

def update_lcd(message):
    print("Updating LCD with message:", message)
    lcd_string(message, LCD_LINE_1)


# LCD mode
LCD_CHR = 1  # LCD command
LCD_CMD = 0  # LCD data

# LCD flags
LCD_BACKLIGHT = 0x08  # On
ENABLE = 0b00000100  # Enable bit

# Initialize encoder
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLOCK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DATA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize global variables
current_state = GPIO.input(DATA_PIN)
previous_state = current_state

# Define a callback function for rotary encoder
def rotary_callback(channel):
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

# Start station
def start_station(station_index):
    global player_process
    try:
        # Stop the previous station
        stop_player()

        # Start the new station
        player_process = subprocess.Popen(["ffmpeg", "-i", STATIONS[station_index]["url"], "-f", "alsa", "default"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Now playing: {STATIONS[station_index]['name']}")
        update_lcd(STATIONS[station_index]['name'])  # Display the station name
    except OSError as e:
        print(f"Error launching ffmpeg: {e}")

# Stop player
def stop_player():
    global player_process
    if player_process:
        player_process.kill()
        player_process = None

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
    stop_player()  # Stop ffmpeg on exit
