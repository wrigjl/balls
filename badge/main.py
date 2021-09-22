import ssd1306
import network
import time
import machine
import config
import neopixel
import ubinascii
import urequests
import json
import bad_funcs as bf

# Init our button input and output...
button_read = machine.ADC(0)
button_out = machine.Pin(16, machine.Pin.OUT)

# Init neopixels for badge
num_pixels = 2
neo_pix_pin = machine.Pin(0)
np = bf.init_neopix(neo_pix_pin, num_pixels)

# Init the display for our use...
display = bf.init_display()
display.text('BSides IF 2021', 0, 0, 1)
display.show()

# Do some shit with the serial port (Disable it? Hell I don't know yet...)
# bf.set_serial()

net_sta = bf.network_connect(display)
api_id = bf.get_cli_id(net_sta)
# Init a counter for our use instead of sleep which just screws us over
counter = 1
url_string = "http://balls.thought.net:8080/poll/%s" % api_id
tmp_pwn = "http://balls.thought.net:8080/toss/%s" % api_id
# This is our main game loop now... This is where the real work is going to be.
while True:
    if counter % 200 == 0:
        print("Counter is:%s" % counter)
        bf.demo(np)
    if counter % 1000 == 0:
        bf.default_display(display)
        deets = bf.get_deets(url_string)
        print("Deets be gotten...\n%s" % deets)
        if deets['Hasball']:
            pwnd = bf.get_deets(tmp_pwn)
            print("Pwn Activated:\n%s" % pwnd)
    if bf.check_button(button_read, button_out):
        display.fill(0) # Any time we want to display stuff we need to clear it
        display.text('Button Pressed!', 0, 0, 1)
        display.show()
        time.sleep(5)
    # else:
    #     display.fill(0)
    #     display.text('Not Button IF Stuff', 0, 0, 1)
    #     display.show()
    #     time.sleep(5)
    if counter % 60000 == 0:
        counter = 0
    counter = counter + 1
