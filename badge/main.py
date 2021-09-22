
import ssd1306
import network
import time
import machine
import config


button_read = machine.ADC(0)
button_out = machine.Pin(16, Pin.OUT)


def check_button():
    button_out(1)
    test_val = 0
    for each in range(10):
        test_val += button_read.read()
    test_val = test_val / 10
    if test_val > 10:
        print("button pressed")
    else:
        print("button not pressed")
    button_out(0)


def set_serial():
    from machine import UART
    uart = UART(0, baudrate=config.baud)
    uart.write('moo')


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


display = init_display()
display.text('BSides IF 2021', 0, 0, 1)
display.show()


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


set_serial()
network_connect(display)
