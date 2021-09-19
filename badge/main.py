
import ssd1306
import network
import time
import machine
import config


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
