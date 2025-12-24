#!/usr/bin/env python3
"""
Test DHT11 sensor connection and basic reading.
Run this first to verify your wiring works.
"""
import time
import board
import adafruit_dht

# Initialize DHT11 on GPIO4 (physical pin 7)
sensor = adafruit_dht.DHT11(board.D4)

print("DHT11 Sensor Test")
print("Press Ctrl+C to exit\n")

try:
    while True:
        try:
            temp_c = sensor.temperature
            humidity = sensor.humidity
            
            if temp_c is not None and humidity is not None:
                temp_f = temp_c * 9/5 + 32
                print(f"Temp: {temp_c:.1f}°C ({temp_f:.1f}°F) | Humidity: {humidity:.1f}%")
            else:
                print("Sensor returned None - retrying...")
                
        except RuntimeError as e:
            # DHT sensors are finicky, errors are normal
            print(f"Reading error: {e.args[0]}")
            
        time.sleep(2)  # DHT11 can only be read every ~2 seconds

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    sensor.exit()
