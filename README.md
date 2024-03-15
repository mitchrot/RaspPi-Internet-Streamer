This is a Project i made for my gran, its a simple users interface that only uses one Rotary encoder to select a satation 


[Wiring](#wiring.md)


Auto-Start Instructions for Raspberry Pi:

    Create a Service File:
        Open a terminal on your Raspberry Pi.
        Navigate to the /etc/systemd/system directory:

        bash

cd /etc/systemd/system

Create a new service file (e.g., radiostreamer.service) using a text editor such as nano:

bash

    sudo nano radiostreamer.service

Edit the Service File:

    Add the following content to the service file:

    plaintext

    [Unit]
    Description=Radio Streamer Service
    After=network.target

    [Service]
    Type=simple
    ExecStart=/usr/bin/python3 /path/to/your/radiostreamer.py
    WorkingDirectory=/path/to/your
    StandardOutput=inherit
    StandardError=inherit
    Restart=always
    User=pi

    [Install]
    WantedBy=multi-user.target

    Replace /path/to/your with the actual path where radiostreamer.py is located.
    Save the file and exit the text editor.

Enable the Service:

    Reload systemd to pick up the new service file:

    bash

sudo systemctl daemon-reload

Enable the service to start on boot:

bash

    sudo systemctl enable radiostreamer.service

Start the Service:

    Start the service to ensure it runs immediately:

    bash

    sudo systemctl start radiostreamer.service

Verify Status:

    Check the status of the service to ensure it's running without errors:

    bash

    sudo systemctl status radiostreamer.service

Reboot:

    Reboot your Raspberry Pi to verify that the service starts automatically:

    bash

        sudo reboot

After following these steps, your radiostreamer.py script should start automatically on boot and continue running in the background. Users can access the service status and control it using systemctl commands.
