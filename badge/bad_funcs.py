import ssd1306
import network
import time
import machine
import config
import ubinascii
import urequests
import neopixel
import json

def disp_test(display):
    display.fill(0)
    display.fill_rect(0, 0, 32, 32, 1)
    display.fill_rect(2, 2, 28, 28, 0)
    display.vline(9, 8, 22, 1)
    display.vline(16, 2, 22, 1)
    display.vline(23, 8, 22, 1)
    display.fill_rect(26, 24, 2, 4, 1)
    display.text('MicroPython', 40, 0, 1)
    display.text('SSD1306', 40, 12, 1)
    display.text('OLED 128x64', 40, 24, 1)
    display.show()

def get_deets(url_str):
    response = urequests.get(url_str)
    user_deets = json.loads(response.text)
    response.close()
    return user_deets

def neo_test(np):
    np[0] = (25, 0, 0) # set to red, full brightness
    np[1] = (0, 25, 0) # set to red, full brightness
    np.write()

def check_button(button_read, button_out):
    button_out(1)
    test_val = 0
    for each in range(10):
        test_val += button_read.read()
    test_val = test_val / 10
    if test_val > 30:
        return True
    else:
        return False
    button_out(0)

def frash(np):
    n = np.n
    # bounce
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep_ms(20)
    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()

def fadez(np):
    n = np.n
    # bounce
    # fade in/out
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()
        time.sleep_ms(10)
    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()

def ballzy(np):
    n = np.n
    # cycle
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        np[i % n] = (255, 255, 255)
        np.write()
        time.sleep_ms(50)
    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()

def demo(np):
    n = np.n
    # cycle
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        np[i % n] = (255, 255, 255)
        np.write()
        time.sleep_ms(50)
    # bounce
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep_ms(60)
    # fade in/out
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()
        time.sleep_ms(10)
    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()

def set_serial():
    from machine import UART
    uart = UART(0, baudrate=config.baud)
    uart.write('moo')

def init_neopix(pin_num, pixel_count):
    np = neopixel.NeoPixel(pin_num, pixel_count)
    return np

def init_display():
    sda = machine.Pin(4)
    scl = machine.Pin(5)
    i2c = machine.I2C(scl=scl, sda=sda, freq=400000)
    display = ssd1306.SSD1306_I2C(128, 64, i2c)
    display.fill(1)
    display.show()
    time.sleep(0.5)
    display.fill(0)
    display.show()
    return display

def network_connect(dsp):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    while not sta.isconnected():
        dsp.text('connecting...', 0, 10, 1)
        dsp.show()
        sta.connect(config.ssid, config.ssid_pass)
        time.sleep(5)
    dsp.text('wifi connected', 0, 20, 1)
    dsp.show()
    return sta

def network_recon(sta):
    if not sta.isconnected():
        sta.connect(config.ssid, config.ssid_pass)

def get_cli_id(net):
    mac = ubinascii.hexlify(net.config('mac'),'').decode('hex')
    tmp = []
    for each in mac:
        if each in '0123456789abcdef':
            tmp += each
    mac = ''.join(tmp)
    return mac

def default_display(display, deets):
    score_str = 'Score:%d' % deets['Score']
    uid_str = 'UID:%s' % deets['User']
    display.fill(0) # Any time we want to display stuff we need to clear it
    display.text('Let\'s Play...', 0, 0, 1)
    # display.text('Can you catch?', 0, 10, 1)
    display.text('Press a button', 0, 10, 1)
    display.text('IF you get a', 0, 20, 1)
    display.text('ball...', 0, 30, 1)
    display.text(score_str, 0, 40, 1)
    display.text(uid_str, 0, 50, 1)
    display.show()

def got_a_ball(display):
        display.fill(0) # Any time we want to display stuff we need to clear it
        display.text('You got a BALL!!!', 0, 0, 1)
        display.text('Touch a button', 0, 10, 1)
        display.text('to toss it!', 0, 20, 1)
        display.show()

def tossd_a_ball(display):
        display.fill(0) # Any time we want to display stuff we need to clear it
        display.text('You tossed the', 0, 0, 1)
        display.text('ball!', 0, 10, 1)
        display.text('Hope it scored!', 0, 20, 1)
        display.show()

def cheetz(display):
        display.fill(0) # Any time we want to display stuff we need to clear it
        display.text('You CHEATER!', 0, 0, 1)
        display.text('Nice Job!', 0, 10, 1)
        display.text('Hope it was fun!', 0, 20, 1)
        display.show()
