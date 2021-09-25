#!/bin/bash

esptool.py --no-stub flash_id
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 ./esp8266-20210902-v1.17.bin 
# esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 ~/Downloads/esp8266-20210902-v1.17.bin 
echo "Done flashing now to program..."
echo "Placing boot file..."
ampy -p /dev/ttyUSB0 put boot.py 
echo "Placing boot file... You know... Just in case the first one was a fail..."
ampy -p /dev/ttyUSB0 put boot.py 
echo "Placing bad_funcs file..."
ampy -p /dev/ttyUSB0 put bad_funcs.py 
echo "Placing main file..."
ampy -p /dev/ttyUSB0 put main.py
echo "Placing config file..."
ampy -p /dev/ttyUSB0 put config.py 
echo "Placing test config file..."
ampy -p /dev/ttyUSB0 put ~/config.py 
#esptool.py --no-stub chip_id
# esptool.py --no-stub flash_id
ampy -p /dev/ttyUSB0 ls
# ampy -p /dev/ttyUSB0 run main.py 


esptool.py --no-stub flash_id
esptool.py --port /dev/ttyUSB1 erase_flash
esptool.py --port /dev/ttyUSB1 --baud 460800 write_flash --flash_size=detect 0 ./esp8266-20210902-v1.17.bin 
# esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 ~/Downloads/esp8266-20210902-v1.17.bin 
echo "Done flashing now to program..."
echo "Placing boot file..."
ampy -p /dev/ttyUSB1 put boot.py 
echo "Placing boot file... You know... Just in case the first one was a fail..."
ampy -p /dev/ttyUSB1 put boot.py 
echo "Placing bad_funcs file..."
ampy -p /dev/ttyUSB1 put bad_funcs.py 
echo "Placing main file..."
ampy -p /dev/ttyUSB1 put main.py
echo "Placing config file..."
ampy -p /dev/ttyUSB1 put config.py 
echo "Placing test config file..."
ampy -p /dev/ttyUSB1 put ~/config.py 
#esptool.py --no-stub chip_id
# esptool.py --no-stub flash_id
ampy -p /dev/ttyUSB1 ls
# ampy -p /dev/ttyUSB0 run main.py 
