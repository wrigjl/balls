import ssd1306
import network
import time
import machine
import config
import neopixel
import bad_funcs as bf

# Init our button input and output...
button_read = machine.ADC(0)
button_out = machine.Pin(16, machine.Pin.OUT)

# Init neopixels for badge
# These are still a bit BROKE...
num_pixels = 2
neo_pix_pin = machine.Pin(0)
np = bf.init_neopix(neo_pix_pin, num_pixels)

# Init the display for our use...
display = bf.init_display()
display.text('BSides IF 2021', 0, 0, 1)
display.show()

# Do some shit with the serial port (Disable it? Hell I don't know yet...)
# bf.set_serial()

bf.network_connect(display)

# Init a counter for our use instead of sleep which just screws us over
counter = 1

# This is our main game loop now... This is where the real work is going to be.
while True:
    if counter % 200 == 0:
        print("Counter is:%s" % counter)
    if counter % 1000 == 0:
        bf.default_display(display)
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
    if counter % 50000 == 0:
        counter = 0
    counter = counter + 1
    # np[0] = (25, 0, 0) # set to red, full brightness
    # np[1] = (0, 25, 0) # set to red, full brightness
    # np.write()
    # np[0] = (0, 25, 0) # set to red, full brightness
    # np[1] = (25, 25, 0) # set to red, full brightness
    # np.write()
    # neo_test(np)
    # demo(np)
# while True:
        # display.show()
    # time.sleep(.5)
    # time.sleep(1.5)
