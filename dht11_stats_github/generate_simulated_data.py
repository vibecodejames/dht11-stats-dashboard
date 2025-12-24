#!/usr/bin/env python3
"""
Generate realistic overnight DHT11 data for San Diego, CA
Cold winter day - Late December

REALISTIC INDOOR PATTERN:
- Evening (10 PM): House still warm from daytime heating, ~23°C
- Night (11 PM - 2 AM): Gradual cooling as heating off or setback
- Coldest (5-6 AM): Right before sunrise, house at coldest
- Morning (6 AM+): Heating kicks on or sun starts warming

San Diego December reality:
- Outdoor overnight low: ~9°C (48°F) around 5-6 AM  
- Outdoor high: ~18°C (65°F) around 2-3 PM
- Indoor with typical heating: 18-23°C (65-73°F)
- Humidity: 55-75% (higher at night when cooler)

Based on James's actual readings:
- Baseline temp: 23.3°C at ~10 PM (house still warm)
- Baseline humidity: 57%
"""

import csv
import random
import math
from datetime import datetime, timedelta

# Configuration
START_TIME = datetime(2024, 12, 23, 22, 0, 0)  # 10 PM
DURATION_HOURS = 8
SAMPLE_INTERVAL_SECONDS = 10
OUTPUT_FILE = "sensor_data.csv"

# Based on James's actual readings at 10 PM
EVENING_TEMP = 23.3  # °C - warm house in evening
COLDEST_TEMP = 19.5  # °C - house cools to this by 5-6 AM (around 67°F)
EVENING_HUMIDITY = 57  # %
NIGHT_HUMIDITY_PEAK = 68  # % - humidity rises as temp drops


def get_outdoor_temp(hour):
    """
    Approximate outdoor temperature for San Diego December night.
    Coldest around 5-6 AM.
    """
    # Hour is 0-23
    if hour >= 22 or hour < 6:
        # Nighttime cooling curve
        if hour >= 22:
            hours_since_10pm = hour - 22
        else:
            hours_since_10pm = hour + 2
        
        # Outdoor goes from ~14°C at 10 PM to ~9°C at 6 AM
        outdoor = 14 - (hours_since_10pm / 8) * 5
        return outdoor
    else:
        return 9  # Early morning low


def simulate_indoor_temp(minutes_elapsed):
    """
    Simulate realistic indoor temperature overnight.
    
    Key insight: Indoor temp follows outdoor with lag and damping.
    House thermal mass means indoor changes slowly.
    
    Pattern:
    - 10 PM: 23.3°C (your actual reading)
    - 11 PM: 22.8°C (starting to cool)
    - 1 AM: 22.0°C
    - 3 AM: 21.0°C  
    - 5 AM: 20.0°C (approaching minimum)
    - 6 AM: 19.5°C (coldest - just before sunrise/heating)
    """
    total_minutes = minutes_elapsed
    total_hours = total_minutes / 60
    
    # Temperature drop is NOT linear - it follows Newton's law of cooling
    # Rate of cooling slows as indoor approaches outdoor
    
    # Simple exponential decay model
    # T(t) = T_outdoor + (T_initial - T_outdoor) * e^(-kt)
    
    outdoor_approx = 10  # Average overnight outdoor
    k = 0.08  # Cooling constant (house loses heat slowly)
    
    temp = outdoor_approx + (EVENING_TEMP - outdoor_approx) * math.exp(-k * total_hours)
    
    # Add HVAC cycling (if heating kicks in periodically)
    # Small bumps every ~2 hours as thermostat triggers
    hvac_cycle_minutes = 120
    cycle_position = (total_minutes % hvac_cycle_minutes) / hvac_cycle_minutes
    
    # HVAC runs for ~20% of cycle, adds warmth
    if cycle_position < 0.2:
        hvac_boost = 0.3 * math.sin(cycle_position / 0.2 * math.pi)
    else:
        hvac_boost = 0
    
    # Random sensor noise (DHT11 is ±1°C but indoor is stable)
    noise = random.gauss(0, 0.1)
    
    temp = temp + hvac_boost + noise
    
    # Round to 0.1°C (DHT11 resolution)
    return round(temp, 1)


def simulate_humidity(minutes_elapsed, current_temp):
    """
    Simulate humidity - inversely correlated with temperature.
    
    Physics: As air cools, relative humidity increases
    (same absolute moisture, lower saturation point)
    
    Also: People breathing adds moisture overnight
    """
    total_hours = minutes_elapsed / 60
    
    # Base humidity increases as temp drops
    # Using inverse relationship with temperature
    temp_factor = (EVENING_TEMP - current_temp) * 2.5  # ~2.5% RH per degree C drop
    
    # Moisture buildup from breathing (slow accumulation)
    breath_moisture = total_hours * 0.5  # +0.5% per hour
    
    # Random variation
    noise = random.gauss(0, 1.5)
    
    humidity = EVENING_HUMIDITY + temp_factor + breath_moisture + noise
    
    # Clamp to realistic range
    humidity = max(50, min(78, humidity))
    
    return round(humidity)


def add_realistic_events(readings):
    """
    Add realistic overnight events:
    - Person gets up (body heat spike near sensor)
    - HVAC turning on (gradual temp rise)
    - Window/door draft (brief temp dip)
    """
    events = []
    
    # Bathroom trip ~2 AM (4 hours in = 1440 readings at 10s interval)
    bathroom_idx = random.randint(1400, 1500)
    events.append(('body_heat', bathroom_idx, 25))
    
    # Another trip ~5 AM
    bathroom_idx2 = random.randint(2400, 2520)
    events.append(('body_heat', bathroom_idx2, 20))
    
    # Brief cold draft (someone checks window/thermostat) ~3 AM
    draft_idx = random.randint(1700, 1900)
    events.append(('draft', draft_idx, 15))
    
    for event_type, start_idx, duration in events:
        for i in range(duration):
            idx = start_idx + i
            if idx >= len(readings):
                break
            
            timestamp, temp, humidity = readings[idx]
            
            # Smooth ramp up and down
            progress = i / duration
            spike = math.sin(progress * math.pi)  # 0 -> 1 -> 0
            
            if event_type == 'body_heat':
                # Person walks by - temp and humidity spike
                temp += 2.0 * spike
                humidity += 10 * spike
            elif event_type == 'draft':
                # Cold air - temp drops, humidity might drop too
                temp -= 1.0 * spike
                humidity -= 5 * spike
            
            readings[idx] = (timestamp, round(temp, 1), round(max(45, min(85, humidity))))
    
    return readings


def generate_data():
    """Generate full overnight dataset"""
    readings = []
    
    current_time = START_TIME
    end_time = START_TIME + timedelta(hours=DURATION_HOURS)
    
    minutes_elapsed = 0
    
    while current_time < end_time:
        temp = simulate_indoor_temp(minutes_elapsed)
        humidity = simulate_humidity(minutes_elapsed, temp)
        
        readings.append((current_time.isoformat(), temp, humidity))
        
        current_time += timedelta(seconds=SAMPLE_INTERVAL_SECONDS)
        minutes_elapsed = (current_time - START_TIME).total_seconds() / 60
    
    # Add random realistic events
    readings = add_realistic_events(readings)
    
    return readings


def save_to_csv(readings, filename):
    """Save readings to CSV"""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'temperature_c', 'humidity_pct'])
        for timestamp, temp, humidity in readings:
            writer.writerow([timestamp, temp, humidity])


def print_summary(readings):
    """Print summary with hourly breakdown"""
    temps = [r[1] for r in readings]
    humidities = [r[2] for r in readings]
    
    print(f"\n{'='*60}")
    print(f"Generated {len(readings)} readings")
    print(f"Time range: {readings[0][0]} to {readings[-1][0]}")
    print(f"{'='*60}")
    
    print(f"\nOverall Statistics:")
    print(f"  Temperature: {min(temps):.1f}°C to {max(temps):.1f}°C (mean: {sum(temps)/len(temps):.1f}°C)")
    print(f"  Humidity: {min(humidities)}% to {max(humidities)}% (mean: {sum(humidities)/len(humidities):.0f}%)")
    
    print(f"\nHourly Breakdown:")
    print(f"  {'Hour':<8} {'Avg Temp':<12} {'Avg Humidity':<12}")
    print(f"  {'-'*32}")
    
    # Group by hour
    hourly_data = {}
    for timestamp, temp, humidity in readings:
        hour = datetime.fromisoformat(timestamp).strftime("%I %p")
        if hour not in hourly_data:
            hourly_data[hour] = {'temps': [], 'humidities': []}
        hourly_data[hour]['temps'].append(temp)
        hourly_data[hour]['humidities'].append(humidity)
    
    for hour, data in hourly_data.items():
        avg_temp = sum(data['temps']) / len(data['temps'])
        avg_hum = sum(data['humidities']) / len(data['humidities'])
        print(f"  {hour:<8} {avg_temp:.1f}°C        {avg_hum:.0f}%")


if __name__ == "__main__":
    print("Generating realistic overnight data for San Diego, CA...")
    print(f"Cold winter night - December 23-24, 2024")
    print(f"Starting conditions: {EVENING_TEMP}°C, {EVENING_HUMIDITY}% RH")
    
    readings = generate_data()
    save_to_csv(readings, OUTPUT_FILE)
    print_summary(readings)
    
    print(f"\n✓ Saved to {OUTPUT_FILE}")
    print("\nNext steps:")
    print("  python stats_analysis.py")
    print("  python visualize.py")
