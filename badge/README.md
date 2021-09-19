
# Prepare Environment

```
python -m venv .venv
. .venv/bin/activate
pip install esptool
pip install adafruit-ampy
```

# Get the firmware

Micropython for the ESP8266 is [here](https://micropython.org/download/esp8266/)

```
wget https://micropython.org/resources/firmware/esp8266-20210902-v1.17.bin
```

# Flash the board

```
$ esptool --port /dev/ttyUSB0 --baud 1000000 write\_flash --flash\_size=4MB -fm dio 0 esp8266-20210902-v1.17.bin
esptool.py v2.8
Serial port /dev/ttyUSB0
Connecting....
Detecting chip type... ESP8266
Chip is ESP8266EX
Features: WiFi
Crystal is 26MHz
MAC: 48:3f:da:9d:2e:a0
WARNING: ROM doesn't support changing baud rate. Keeping initial baud rate 115200
Enabling default SPI flash mode...
Configuring flash size...
Erasing flash...
Flash params set to 0x0240
Took 2.87s to erase flash block
Wrote 633856 bytes at 0x00000000 in 62.7 seconds (80.8 kbit/s)...

Leaving...
Hard resetting via RTS pin...
```

# Install the python code

```
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put config.py
```

Then press the reset button. Note: if you want to connect to your own
SSID, edit appropriate strings in `config.py` first.
