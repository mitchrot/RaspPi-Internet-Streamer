Wiring Instructions:
Components Needed:

    Raspberry Pi Zero 2 W
    I2C LCD Display (LCD 16X2 LCD with I2C Interface)
    Rotary Encoder (KY-040 rotary encoder)
    Jumper wires (This Project was Soldered)

Wiring Steps:

    I2C LCD Display:
        Connect the VCC pin of the LCD display to the 5V pin on the Raspberry Pi.
        Connect the GND pin of the LCD display to any GND pin on the Raspberry Pi.
        Connect the SDA pin of the LCD display to the SDA pin (GPIO2) on the Raspberry Pi.
        Connect the SCL pin of the LCD display to the SCL pin (GPIO3) on the Raspberry Pi.

    Rotary Encoder:
        Connect the CLK pin of the rotary encoder to any GPIO pin on the Raspberry Pi (e.g., GPIO27).
        Connect the DT pin of the rotary encoder to any GPIO pin on the Raspberry Pi (e.g., GPIO22).
        Connect the SW pin (if available) of the rotary encoder to any GPIO pin on the Raspberry Pi for the push-button functionality.

    Power Supply:
        Connect the 5V pin of the Raspberry Pi to the positive rail of your breadboard.
        Connect any GND pin of the Raspberry Pi to the negative rail of your breadboard.

    Optional: LCD Backlight Control:
        If your LCD display has a backlight that you want to control, connect the control pin to any GPIO pin on the Raspberry Pi (e.g., GPIO4).

    Final Connections:
        Double-check all connections to ensure they are secure and properly connected.
        Make sure there are no loose wires or short circuits.
        Power on your Raspberry Pi and test the functionality of the LCD display and rotary encoder.

Once all connections are made and verified, you should be ready to use your Raspberry Pi Zero 2 W with the radiostreamer.py script. Make sure to adjust the GPIO pins in the script if you've used different pins for the LCD display and rotary encoder.
