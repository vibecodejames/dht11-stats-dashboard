#!/usr/bin/env python3
"""
Collect DHT11 sensor data and save to CSV.
This is your data pipeline - treat it like production code.
"""
import time
import csv
import os
from datetime import datetime
import board
import adafruit_dht

# Configuration
SENSOR_PIN = board.D4
SAMPLE_INTERVAL = 10  # seconds between readings
OUTPUT_FILE = "sensor_data.csv"
READINGS_TARGET = 500  # how many readings to collect


class DataCollector:
    def __init__(self, output_file):
        self.sensor = adafruit_dht.DHT11(SENSOR_PIN)
        self.output_file = output_file
        self.readings_count = 0
        self.errors_count = 0
        
        # Create CSV with headers if it doesn't exist
        if not os.path.exists(output_file):
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'temperature_c', 'humidity_pct'])
    
    def read_sensor(self):
        """Attempt to read sensor, return (temp, humidity) or (None, None)"""
        try:
            temp = self.sensor.temperature
            humidity = self.sensor.humidity
            if temp is not None and humidity is not None:
                return temp, humidity
        except RuntimeError:
            pass
        return None, None
    
    def collect_single(self):
        """Collect one valid reading, retrying up to 5 times"""
        for attempt in range(5):
            temp, humidity = self.read_sensor()
            if temp is not None:
                return temp, humidity
            time.sleep(0.5)
        
        self.errors_count += 1
        return None, None
    
    def save_reading(self, temp, humidity):
        """Append reading to CSV"""
        timestamp = datetime.now().isoformat()
        with open(self.output_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, temp, humidity])
        self.readings_count += 1
    
    def run(self, target_readings):
        """Main collection loop"""
        print(f"Starting data collection...")
        print(f"Target: {target_readings} readings")
        print(f"Interval: {SAMPLE_INTERVAL} seconds")
        print(f"Output: {self.output_file}")
        print(f"Estimated time: {(target_readings * SAMPLE_INTERVAL) / 60:.1f} minutes")
        print("-" * 50)
        
        try:
            while self.readings_count < target_readings:
                temp, humidity = self.collect_single()
                
                if temp is not None:
                    self.save_reading(temp, humidity)
                    progress = (self.readings_count / target_readings) * 100
                    print(f"[{self.readings_count}/{target_readings}] "
                          f"Temp: {temp}°C, Humidity: {humidity}% "
                          f"({progress:.1f}% complete)")
                else:
                    print(f"[{self.readings_count}/{target_readings}] "
                          f"Read failed (total errors: {self.errors_count})")
                
                time.sleep(SAMPLE_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\nCollection interrupted by user")
        finally:
            self.sensor.exit()
            print(f"\nCollection complete!")
            print(f"Total readings: {self.readings_count}")
            print(f"Total errors: {self.errors_count}")
            print(f"Error rate: {(self.errors_count / max(1, self.readings_count + self.errors_count)) * 100:.1f}%")


if __name__ == "__main__":
    collector = DataCollector(OUTPUT_FILE)
    collector.run(READINGS_TARGET)
