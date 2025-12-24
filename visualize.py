#!/usr/bin/env python3
"""
Visualization of sensor data and statistics.
Creates publication-quality charts.
"""
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from stats_analysis import (
    load_data, mean, std_dev, quartiles, 
    frequency_distribution, correlation
)


def setup_style():
    """Set consistent plot style"""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12


def plot_time_series(temps, humidities, timestamps, output_file='01_timeseries.png'):
    """Plot temperature and humidity over time"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    # Parse timestamps
    times = [datetime.fromisoformat(ts) for ts in timestamps]
    
    # Temperature
    ax1.plot(times, temps, 'b-', alpha=0.7, linewidth=0.8)
    ax1.axhline(mean(temps), color='red', linestyle='--', label=f'Mean: {mean(temps):.1f}°C')
    ax1.fill_between(times, 
                     [mean(temps) - std_dev(temps)] * len(times),
                     [mean(temps) + std_dev(temps)] * len(times),
                     alpha=0.2, color='red', label=f'±1 Std Dev')
    ax1.set_ylabel('Temperature (°C)')
    ax1.legend(loc='upper right')
    ax1.set_title('Temperature Over Time')
    
    # Humidity
    ax2.plot(times, humidities, 'g-', alpha=0.7, linewidth=0.8)
    ax2.axhline(mean(humidities), color='darkgreen', linestyle='--', 
                label=f'Mean: {mean(humidities):.1f}%')
    ax2.set_ylabel('Humidity (%)')
    ax2.set_xlabel('Time')
    ax2.legend(loc='upper right')
    ax2.set_title('Humidity Over Time')
    
    # Format x-axis
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_histograms(temps, humidities, output_file='02_histograms.png'):
    """Plot histograms showing frequency distributions"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Temperature histogram
    ax1.hist(temps, bins=15, edgecolor='black', alpha=0.7, color='steelblue')
    ax1.axvline(mean(temps), color='red', linestyle='--', linewidth=2, 
                label=f'Mean: {mean(temps):.2f}°C')
    ax1.axvline(np.median(temps), color='orange', linestyle=':', linewidth=2,
                label=f'Median: {np.median(temps):.2f}°C')
    ax1.set_xlabel('Temperature (°C)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Temperature Distribution')
    ax1.legend()
    
    # Humidity histogram
    ax2.hist(humidities, bins=15, edgecolor='black', alpha=0.7, color='seagreen')
    ax2.axvline(mean(humidities), color='red', linestyle='--', linewidth=2,
                label=f'Mean: {mean(humidities):.2f}%')
    ax2.set_xlabel('Humidity (%)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Humidity Distribution')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_boxplots(temps, humidities, output_file='03_boxplots.png'):
    """Box plots showing quartiles and outliers"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Temperature boxplot
    bp1 = ax1.boxplot(temps, patch_artist=True)
    bp1['boxes'][0].set_facecolor('steelblue')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_title('Temperature Distribution\n(Box shows Q1, Median, Q3)')
    ax1.set_xticklabels([''])
    
    # Add annotations
    q1, q2, q3 = quartiles(temps)
    ax1.annotate(f'Q3: {q3:.1f}', xy=(1.1, q3), fontsize=10)
    ax1.annotate(f'Median: {q2:.1f}', xy=(1.1, q2), fontsize=10)
    ax1.annotate(f'Q1: {q1:.1f}', xy=(1.1, q1), fontsize=10)
    
    # Humidity boxplot
    bp2 = ax2.boxplot(humidities, patch_artist=True)
    bp2['boxes'][0].set_facecolor('seagreen')
    ax2.set_ylabel('Humidity (%)')
    ax2.set_title('Humidity Distribution')
    ax2.set_xticklabels([''])
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_correlation(temps, humidities, output_file='04_correlation.png'):
    """Scatter plot showing correlation between temp and humidity"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.scatter(temps, humidities, alpha=0.5, s=30, c='purple', edgecolors='black', linewidth=0.5)
    
    # Add trend line
    z = np.polyfit(temps, humidities, 1)
    p = np.poly1d(z)
    temp_range = np.linspace(min(temps), max(temps), 100)
    ax.plot(temp_range, p(temp_range), 'r--', linewidth=2, 
            label=f'Trend line (r = {correlation(temps, humidities):.3f})')
    
    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Humidity (%)')
    ax.set_title('Temperature vs Humidity Correlation')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_probability_density(temps, output_file='05_pdf.png'):
    """Probability density function vs normal distribution"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Histogram normalized to probability density
    n, bins, patches = ax.hist(temps, bins=20, density=True, alpha=0.7, 
                                color='steelblue', edgecolor='black',
                                label='Observed Distribution')
    
    # Overlay theoretical normal distribution
    mu = mean(temps)
    sigma = std_dev(temps)
    x = np.linspace(min(temps) - sigma, max(temps) + sigma, 100)
    normal_pdf = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)
    ax.plot(x, normal_pdf, 'r-', linewidth=2, 
            label=f'Normal Distribution\n(μ={mu:.2f}, σ={sigma:.2f})')
    
    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Probability Density')
    ax.set_title('Observed vs Theoretical Normal Distribution')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_rolling_statistics(temps, timestamps, window=20, output_file='06_rolling.png'):
    """Plot rolling mean and standard deviation"""
    from stats_analysis import rolling_mean, rolling_std
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    # Parse timestamps (only for valid rolling window range)
    times = [datetime.fromisoformat(ts) for ts in timestamps]
    roll_times = times[window-1:]  # Rolling stats have fewer points
    
    # Calculate rolling statistics
    roll_mean = rolling_mean(temps, window)
    roll_std = rolling_std(temps, window)
    
    # Rolling mean
    ax1.plot(times, temps, 'b-', alpha=0.3, linewidth=0.5, label='Raw data')
    ax1.plot(roll_times, roll_mean, 'r-', linewidth=2, label=f'Rolling mean (window={window})')
    ax1.set_ylabel('Temperature (°C)')
    ax1.legend(loc='upper right')
    ax1.set_title(f'Rolling Mean (Window = {window} samples)')
    
    # Rolling std dev
    ax2.plot(roll_times, roll_std, 'g-', linewidth=2)
    ax2.axhline(std_dev(temps), color='red', linestyle='--', 
                label=f'Overall std dev: {std_dev(temps):.2f}°C')
    ax2.set_ylabel('Standard Deviation (°C)')
    ax2.set_xlabel('Time')
    ax2.legend(loc='upper right')
    ax2.set_title(f'Rolling Standard Deviation (Window = {window} samples)')
    
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def create_all_visualizations(filename='sensor_data.csv'):
    """Generate all visualization plots"""
    setup_style()
    
    temps, humidities, timestamps = load_data(filename)
    
    print(f"\nGenerating visualizations for {len(temps)} data points...")
    print("-" * 50)
    
    plot_time_series(temps, humidities, timestamps)
    plot_histograms(temps, humidities)
    plot_boxplots(temps, humidities)
    plot_correlation(temps, humidities)
    plot_probability_density(temps)
    
    # Only do rolling stats if we have enough data
    if len(temps) >= 30:
        plot_rolling_statistics(temps, timestamps, window=20)
    
    print("-" * 50)
    print("All visualizations complete!")
    print(f"\nGenerated files:")
    print("  01_timeseries.png  - Temperature and humidity over time")
    print("  02_histograms.png  - Frequency distributions")
    print("  03_boxplots.png    - Quartile visualization")
    print("  04_correlation.png - Temp vs humidity scatter")
    print("  05_pdf.png         - Probability density comparison")
    if len(temps) >= 30:
        print("  06_rolling.png     - Rolling statistics")


if __name__ == "__main__":
    import sys
    
    filename = sys.argv[1] if len(sys.argv) > 1 else "sensor_data.csv"
    
    # Install matplotlib if not present
    try:
        import matplotlib
    except ImportError:
        import subprocess
        subprocess.run(['pip', 'install', 'matplotlib', 'numpy'])
        import matplotlib
    
    create_all_visualizations(filename)
