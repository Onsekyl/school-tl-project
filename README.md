# Telecommunication and Machine Learning Project
> [!IMPORTANT]
> IN PROGRESS

1. Collect acceleration data with GY-61 ADXL335 accelerometer and Nordic Semiconductor's nRF5340DK dev kit.
2. Send the data to Raspberry Pi 3 using Bluetooth Low Energy.
3. Raspberry Pi 3 forwards the data to a MySQL database which is located at the linux server in a campus network.
4. Fetch the collected orientation/acceleration data to a PC and use it for machine learning (Python, K-Means algorithm).
5. The end goal for the model is to recognise the correct orientation from the data.

# Architecture
TODO: INSERT THE FINAL ARCHITECTURE DIAGRAM

# Core Components
- Nordic Semiconductor's nRF5340DK
- Raspberry Pi 3
- GY-61 ADXL335 accelerometer
- Linux server with the MySQL database
- End PC for the machine learning work

# Used Telecommunication Protocols
- Bluetooth Low Energy
- TCP over HTTP
- Ethernet
- Wi-Fi (end PC connection to the campus network)

