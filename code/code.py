import analogio # type: ignore
import alarm # type: ignore
import board # type: ignore
import digitalio # type: ignore
import time

from adafruit_bme280 import basic as adafruit_bme280 # type: ignore
from adafruit_max1704x import adafruit_max1704x # type: ignore
from adafruit_neopixel import neopixel # type: ignore

"""
I2C devices
"""
i2c = board.I2C()  # uses board.SCL and board.SDA

max17048 = adafruit_max1704x.MAX17048(i2c)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

"""
Capacitive soil moisture sensor v1.2
"""
# Soil sensor #1 on ADC2 CH2
soil_one = analogio.AnalogIn(board.D13)
soil_one_dry = 33204
soil_one_wet = 15589

"""
Neopixel on the board
"""
pixel_power = digitalio.DigitalInOut(board.NEOPIXEL_POWER)
pixel_power.switch_to_output(value=False)
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

"""
TFT display on the board. 
This pin is automatically pulled high in both CircuitPython and Arduino.
"""
tft_power = digitalio.DigitalInOut(board.TFT_I2C_POWER)
tft_power.switch_to_output(value=True)

def soil_moisture(analog_value: int, dry_value=33204, wet_value=15589) -> int|bool:
    """
    Returns soil moisture percentage for an ADC reading in between dry and wet.
    If the value is outside the range, it returns None.
    Higher analog value means drier soil.
    """
    
    if analog_value < wet_value or analog_value > dry_value:
        # Invalid value
        return None
    
    # Map analog value to percentage between wet and dry values
    percentage = int((1 - (analog_value - wet_value) / (dry_value - wet_value)) * 100)
    
    # Clamp to 0-100
    return max(0, min(100, percentage))

def update_pixel_on_percentage(percent: int, brightness=0.1) -> None:
    # Set the pixel color based on the percentage, higher percentage is better
    pixel.fill((255 * percent/100  * brightness, 255 * (1-(percent/100)) * brightness, 0))

while True:
    time.sleep(3)
    print("Battery Voltage: %.2f V" % max17048.cell_voltage)
    print("Battery Charge: %.2f %%" % max17048.cell_percent)
    
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.humidity)
    print("Pressure: %0.1f hPa" % bme280.pressure)
    
    soil_one_adc_val = soil_one.value
    soil_percent = soil_moisture(soil_one_adc_val)
    if not soil_percent:
        print("\nInvalid soil moisture value: %d" % soil_one_adc_val)
    else:
        print("\nSoil Moisture: %0.1f %% (ADC: %d)" % (soil_percent, soil_one_adc_val))
        
        # Update LED
        update_pixel_on_percentage(soil_percent)
        
    time.sleep(6)
        
    seconds_to_sleep = 10

    # Turn off neopixel and TFT display
    # pixel_power.value = False
    tft_power.value = False
    
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + seconds_to_sleep)
    
    # Do a light sleep until the alarm wakes us.
    alarm.light_sleep_until_alarms(time_alarm)
    
    # Finished sleeping. Continue from here.
    # pixel_power.value = True
    tft_power.value = True
    
    # Clear the print output on the TFT display
    print("\n" * 10)