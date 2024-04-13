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
bme280.sea_level_pressure = 1018.8 # hPa

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
pixel_power.value = True

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

"""
TFT display on the board. 
This pin is automatically pulled high in both CircuitPython and Arduino.
"""
tft_power = digitalio.DigitalInOut(board.TFT_I2C_POWER)
tft_power.switch_to_output(value=True)
tft_power.value = True

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

def disable_peripherals() -> None:
    """
    Disables power to the neopixel and display.
    """
    # pixel_power.value = False
    tft_power.value = False

def hibernate(seconds: int) -> None:
    """
    Disables power to the neopixel and display to save power.
    """
    
    disable_peripherals()
    
    """
    If a program does a light sleep, it still goes to sleep but continues
    running the program, resuming after the statement that did the light sleep.
    Power consumption will be minimized. However, on some boards, such as the 
    ESP32-S2, light sleep does not save power compared with using time.sleep().
    """
    
    time.sleep(seconds)
    
def update_pixel_on_percentage(percent: int, brightness=0.1) -> None:
    # Set the pixel color based on the percentage, higher percentage is better
    pixel[0] = ((255 * percent/100  * brightness, 255 * (1-(percent/100)) * brightness, 0))

"""
Main loop
"""

time.sleep(3)

# Check for wake from deep sleep
if alarm.wake_alarm:
    print("Woke up from deep sleep")
    
bat_percent = max(0, min(100, max17048.cell_percent))
    
print(f"Battery Voltage: {max17048.cell_voltage:.1f} V, Charge: {bat_percent:.1f}%")
print(f"Charge Rate: {max17048.charge_rate:.1f}%/h")
print(f"Temperature: {bme280.temperature:.1f} C, Humidity: {bme280.humidity:.1f}%")
print(f"Pressure: {bme280.pressure:.1f} hPa, Altitude: {bme280.altitude:.2f} m")

soil_percent = None

soil_readings = 0
while not soil_percent:
    if soil_readings == 5:
        print("\nFailed to read soil moisture after 5 attempts.")
        break

    time.sleep(1)
    try:
        soil_one_adc_val = soil_one.value
        soil_percent = soil_moisture(soil_one_adc_val)
    except Exception as e:
        # Could be that the ADC was not deinited properly (when testing on the board)
        # Try reconfiguring the ADC pin
        soil_one.deinit()
        time.sleep(0.3)
        soil_one = analogio.AnalogIn(board.D13)
        time.sleep(0.3)
         
    soil_readings += 1
    
if soil_percent:         
    print("Soil Moisture: %0.1f %% (ADC: %d)" % (soil_percent, soil_one_adc_val))

    # Update LED
    update_pixel_on_percentage(soil_percent)

# Allow time for the user to see the readings
time.sleep(6)

seconds_to_sleep = 120

print(f"\nGoing to sleep for {seconds_to_sleep} seconds!")

# Wake up when time is up
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + seconds_to_sleep)

# Wake up when BOOT button is pressed
pin_alarm = alarm.pin.PinAlarm(pin=board.BUTTON, value=False, pull=True)

time.sleep(3)
disable_peripherals()

# Go to deep sleep and wake up when the alarm goes off or the button is pressed
# this will not return and the code will start from the top
alarm.exit_and_deep_sleep_until_alarms(time_alarm, pin_alarm)