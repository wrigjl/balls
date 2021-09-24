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
num_pixels = 8
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
butt_counter = 0
ball_counter = 0
disp_var = 0
url_string = "http://balls.thought.net:8080/poll/%s" % api_id
tmp_pwn = "http://balls.thought.net:8080/toss/%s" % api_id
deets = bf.get_deets(url_string)  # Get our initial deets
pwnd = deets
score_var = deets['Score']
# This is our main game loop now... This is where the real work is going to be.
while True:
    # Display State Machine...
    # Default Display State
    if disp_var == 0:
        bf.default_display(display, deets)
    # Button pressed so we count it down so it stays on the screen for a few seconds...
    elif disp_var == 1:
        if butt_counter > 0:
            butt_counter -= 1
        else:
            disp_var = 0
    # Ball in hand so we count it down so it stays on the screen for a few seconds...
    elif disp_var == 2:
        if ball_counter > 0:
            ball_counter -= 1
        else:
            disp_var = 0
    # Now we change to a time based state machine by using tick counts and do things on a time basis...
    # Every 8 seconds approximately...
    if counter % 100 == 0:
        bf.frash(np)
        # print("Counter is:%s" % counter)
    # Every 30 seconds approximately...
    if counter % 350 == 0:
        bf.network_recon(net_sta)
        bf.fadez(np)
        deets = bf.get_deets(url_string)
        print("Deets be gotten...\n%s" % deets)
        if deets['Hasball']:
            bf.got_a_ball(display)
            bf.ballzy(np)
            ball_counter = 200
            disp_var = 2
    # Cheat unlocked... maybe...
    if pwnd['Hasball']:
        pwnd = bf.get_deets(tmp_pwn)
        bf.cheetz(display)
    if bf.check_button(button_read, button_out):
        if deets['Hasball']:
            pwnd = bf.get_deets(tmp_pwn)
        display.fill(0) # Any time we want to display stuff we need to clear it
        display.text('Button Pressed!', 0, 0, 1)
        if score_var < pwnd['Score']:
            display.text('You Scored!', 0, 10, 1)
        if score_var >= pwnd['Score']:
            display.text('You WHIFFED!', 0, 10, 1)
            display.text('Sorry...', 0, 10, 1)
        display.show()
        butt_counter = 200
        disp_var = 1
    if counter % 60000 == 0:
        counter = 0
    counter = counter + 1
# pwnd = bf.get_deets(tmp_pwn)
