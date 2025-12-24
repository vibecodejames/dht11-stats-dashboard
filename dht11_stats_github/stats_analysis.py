#!/usr/bin/env python3
"""
Statistical analysis of sensor data.
Implement these formulas by hand before using numpy/scipy.

AAI 500 Concepts Covered:
- Descriptive statistics (mean, median, mode, variance, std dev)
- Probability distributions
- Sampling distributions
- Hypothesis testing basics
"""
import csv
import math
from collections import Counter
from datetime import datetime


def load_data(filename):
    """Load CSV data into lists"""
    temps = []
    humidities = []
    timestamps = []
    
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            temps.append(float(row['temperature_c']))
            humidities.append(float(row['humidity_pct']))
            timestamps.append(row['timestamp'])
    
    return temps, humidities, timestamps


# ============================================================
# PART 1: IMPLEMENT DESCRIPTIVE STATISTICS FROM SCRATCH
# ============================================================

def mean(data):
    """
    Calculate arithmetic mean.
    Formula: μ = (1/n) * Σxᵢ
    """
    n = len(data)
    if n == 0:
        return None
    return sum(data) / n


def median(data):
    """
    Calculate median (middle value when sorted).
    For even n: average of two middle values.
    """
    sorted_data = sorted(data)
    n = len(sorted_data)
    
    if n == 0:
        return None
    
    mid = n // 2
    if n % 2 == 0:
        # Even: average of two middle values
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        # Odd: middle value
        return sorted_data[mid]


def mode(data):
    """
    Calculate mode (most frequent value).
    Returns list if multiple modes exist.
    """
    if not data:
        return None
    
    counts = Counter(data)
    max_count = max(counts.values())
    modes = [val for val, count in counts.items() if count == max_count]
    
    return modes[0] if len(modes) == 1 else modes


def variance(data, population=False):
    """
    Calculate variance.
    Population variance: σ² = (1/n) * Σ(xᵢ - μ)²
    Sample variance: s² = (1/(n-1)) * Σ(xᵢ - x̄)²
    
    Use sample variance (population=False) for sensor data.
    """
    n = len(data)
    if n < 2:
        return None
    
    data_mean = mean(data)
    squared_diffs = [(x - data_mean) ** 2 for x in data]
    
    if population:
        return sum(squared_diffs) / n
    else:
        return sum(squared_diffs) / (n - 1)  # Bessel's correction


def std_dev(data, population=False):
    """
    Standard deviation = sqrt(variance)
    """
    var = variance(data, population)
    return math.sqrt(var) if var else None


def range_stat(data):
    """Range = max - min"""
    return max(data) - min(data) if data else None


def quartiles(data):
    """
    Calculate Q1, Q2 (median), Q3.
    Q1 = median of lower half
    Q3 = median of upper half
    """
    sorted_data = sorted(data)
    n = len(sorted_data)
    
    q2 = median(data)
    
    # Split data for Q1 and Q3
    mid = n // 2
    lower_half = sorted_data[:mid]
    upper_half = sorted_data[mid + 1:] if n % 2 else sorted_data[mid:]
    
    q1 = median(lower_half)
    q3 = median(upper_half)
    
    return q1, q2, q3


def iqr(data):
    """Interquartile range = Q3 - Q1"""
    q1, _, q3 = quartiles(data)
    return q3 - q1


def coefficient_of_variation(data):
    """
    CV = (std_dev / mean) * 100
    Useful for comparing variability of different measurements.
    """
    m = mean(data)
    s = std_dev(data)
    if m and s and m != 0:
        return (s / abs(m)) * 100
    return None


# ============================================================
# PART 2: PROBABILITY & DISTRIBUTIONS
# ============================================================

def frequency_distribution(data, bins=10):
    """
    Create frequency distribution (histogram data).
    Returns: list of (bin_center, count, relative_freq)
    """
    min_val = min(data)
    max_val = max(data)
    bin_width = (max_val - min_val) / bins
    
    if bin_width == 0:
        return [(min_val, len(data), 1.0)]
    
    # Initialize bins
    freq = [0] * bins
    
    for x in data:
        # Find which bin this value belongs to
        bin_idx = min(int((x - min_val) / bin_width), bins - 1)
        freq[bin_idx] += 1
    
    # Calculate results
    n = len(data)
    results = []
    for i in range(bins):
        bin_center = min_val + (i + 0.5) * bin_width
        count = freq[i]
        rel_freq = count / n
        results.append((bin_center, count, rel_freq))
    
    return results


def z_score(value, data):
    """
    Calculate z-score: how many std devs from mean.
    z = (x - μ) / σ
    """
    m = mean(data)
    s = std_dev(data)
    if s and s != 0:
        return (value - m) / s
    return None


def detect_outliers_zscore(data, threshold=2.5):
    """
    Find outliers using z-score method.
    Values with |z| > threshold are outliers.
    """
    outliers = []
    for x in data:
        z = z_score(x, data)
        if z and abs(z) > threshold:
            outliers.append((x, z))
    return outliers


def detect_outliers_iqr(data):
    """
    Find outliers using IQR method.
    Outliers are values < Q1 - 1.5*IQR or > Q3 + 1.5*IQR
    """
    q1, _, q3 = quartiles(data)
    iqr_val = q3 - q1
    lower_bound = q1 - 1.5 * iqr_val
    upper_bound = q3 + 1.5 * iqr_val
    
    outliers = [x for x in data if x < lower_bound or x > upper_bound]
    return outliers, lower_bound, upper_bound


# ============================================================
# PART 3: CORRELATION
# ============================================================

def covariance(x_data, y_data):
    """
    Calculate sample covariance between two variables.
    cov(X,Y) = (1/(n-1)) * Σ(xᵢ - x̄)(yᵢ - ȳ)
    """
    n = len(x_data)
    if n != len(y_data) or n < 2:
        return None
    
    x_mean = mean(x_data)
    y_mean = mean(y_data)
    
    products = [(x - x_mean) * (y - y_mean) for x, y in zip(x_data, y_data)]
    return sum(products) / (n - 1)


def correlation(x_data, y_data):
    """
    Pearson correlation coefficient.
    r = cov(X,Y) / (σx * σy)
    
    r = 1: perfect positive correlation
    r = -1: perfect negative correlation
    r = 0: no linear correlation
    """
    cov = covariance(x_data, y_data)
    sx = std_dev(x_data)
    sy = std_dev(y_data)
    
    if cov and sx and sy and sx != 0 and sy != 0:
        return cov / (sx * sy)
    return None


# ============================================================
# PART 4: HYPOTHESIS TESTING
# ============================================================

def one_sample_t_test(data, hypothesized_mean):
    """
    Perform one-sample t-test.
    H0: population mean = hypothesized_mean
    H1: population mean ≠ hypothesized_mean
    
    Returns: t-statistic, degrees of freedom
    
    Example: Test if room temperature differs from 22°C
    """
    n = len(data)
    sample_mean = mean(data)
    sample_std = std_dev(data)
    
    # Standard error of the mean
    se = sample_std / math.sqrt(n)
    
    # t-statistic
    t_stat = (sample_mean - hypothesized_mean) / se
    
    # Degrees of freedom
    df = n - 1
    
    return t_stat, df


def two_sample_t_test(data1, data2):
    """
    Independent two-sample t-test (Welch's t-test).
    H0: population means are equal
    H1: population means differ
    
    Example: Compare day vs night temperatures
    """
    n1, n2 = len(data1), len(data2)
    m1, m2 = mean(data1), mean(data2)
    v1, v2 = variance(data1), variance(data2)
    
    # Welch's t-statistic
    t_stat = (m1 - m2) / math.sqrt(v1/n1 + v2/n2)
    
    # Welch-Satterthwaite degrees of freedom
    df = ((v1/n1 + v2/n2)**2) / ((v1/n1)**2/(n1-1) + (v2/n2)**2/(n2-1))
    
    return t_stat, df


def confidence_interval(data, confidence=0.95):
    """
    Calculate confidence interval for the mean.
    Uses t-distribution approximation.
    
    For 95% CI with large n: mean ± 1.96 * (std/sqrt(n))
    """
    n = len(data)
    sample_mean = mean(data)
    sample_std = std_dev(data)
    se = sample_std / math.sqrt(n)
    
    # t-critical values for common confidence levels (approximate for large n)
    t_critical = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576
    }
    
    t = t_critical.get(confidence, 1.96)
    margin = t * se
    
    return sample_mean - margin, sample_mean + margin


# ============================================================
# PART 5: ROLLING STATISTICS
# ============================================================

def rolling_mean(data, window):
    """Calculate rolling/moving average"""
    result = []
    for i in range(len(data) - window + 1):
        window_data = data[i:i + window]
        result.append(mean(window_data))
    return result


def rolling_std(data, window):
    """Calculate rolling standard deviation"""
    result = []
    for i in range(len(data) - window + 1):
        window_data = data[i:i + window]
        result.append(std_dev(window_data))
    return result


# ============================================================
# MAIN ANALYSIS
# ============================================================

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def analyze_data(filename):
    """Run complete statistical analysis on sensor data"""
    
    temps, humidities, timestamps = load_data(filename)
    n = len(temps)
    
    print(f"\nLoaded {n} readings from {filename}")
    print(f"Time range: {timestamps[0]} to {timestamps[-1]}")
    
    # ---- Temperature Analysis ----
    print_section("TEMPERATURE ANALYSIS (°C)")
    
    print(f"\nDescriptive Statistics:")
    print(f"  Mean:       {mean(temps):.2f}°C")
    print(f"  Median:     {median(temps):.2f}°C")
    print(f"  Mode:       {mode(temps)}°C")
    print(f"  Std Dev:    {std_dev(temps):.3f}°C")
    print(f"  Variance:   {variance(temps):.4f}")
    print(f"  Range:      {range_stat(temps):.1f}°C")
    print(f"  CV:         {coefficient_of_variation(temps):.2f}%")
    
    q1, q2, q3 = quartiles(temps)
    print(f"\nQuartiles:")
    print(f"  Q1 (25%):   {q1:.2f}°C")
    print(f"  Q2 (50%):   {q2:.2f}°C")
    print(f"  Q3 (75%):   {q3:.2f}°C")
    print(f"  IQR:        {iqr(temps):.2f}°C")
    
    ci_low, ci_high = confidence_interval(temps)
    print(f"\n95% Confidence Interval for Mean:")
    print(f"  [{ci_low:.2f}°C, {ci_high:.2f}°C]")
    
    outliers, lower, upper = detect_outliers_iqr(temps)
    print(f"\nOutlier Detection (IQR method):")
    print(f"  Lower bound: {lower:.2f}°C")
    print(f"  Upper bound: {upper:.2f}°C")
    print(f"  Outliers found: {len(outliers)}")
    if outliers:
        print(f"  Values: {outliers[:5]}{'...' if len(outliers) > 5 else ''}")
    
    # ---- Hypothesis Test Example ----
    print(f"\nHypothesis Test: Is mean temperature = 22°C?")
    t_stat, df = one_sample_t_test(temps, 22.0)
    print(f"  t-statistic: {t_stat:.3f}")
    print(f"  Degrees of freedom: {df}")
    print(f"  |t| > 2.0 suggests rejecting H0 at α=0.05")
    if abs(t_stat) > 2.0:
        print(f"  Result: Reject H0 - mean differs significantly from 22°C")
    else:
        print(f"  Result: Fail to reject H0 - insufficient evidence")
    
    # ---- Humidity Analysis ----
    print_section("HUMIDITY ANALYSIS (%)")
    
    print(f"\nDescriptive Statistics:")
    print(f"  Mean:       {mean(humidities):.2f}%")
    print(f"  Median:     {median(humidities):.2f}%")
    print(f"  Mode:       {mode(humidities)}%")
    print(f"  Std Dev:    {std_dev(humidities):.3f}%")
    print(f"  Variance:   {variance(humidities):.4f}")
    print(f"  Range:      {range_stat(humidities):.1f}%")
    
    # ---- Correlation ----
    print_section("CORRELATION ANALYSIS")
    
    r = correlation(temps, humidities)
    print(f"\nPearson correlation (temp vs humidity): {r:.4f}")
    
    if r:
        if abs(r) < 0.3:
            interpretation = "Weak or no linear relationship"
        elif abs(r) < 0.7:
            interpretation = "Moderate linear relationship"
        else:
            interpretation = "Strong linear relationship"
        
        direction = "positive" if r > 0 else "negative"
        print(f"Interpretation: {interpretation} ({direction})")
        
        cov = covariance(temps, humidities)
        print(f"Covariance: {cov:.4f}")
    
    # ---- Frequency Distribution ----
    print_section("FREQUENCY DISTRIBUTION (Temperature)")
    
    freq_dist = frequency_distribution(temps, bins=8)
    print(f"\n{'Bin Center':>12} {'Count':>8} {'Rel Freq':>10} {'Histogram':>20}")
    print("-" * 55)
    for center, count, rel_freq in freq_dist:
        bar = '█' * int(rel_freq * 40)
        print(f"{center:>12.1f} {count:>8} {rel_freq:>10.3f} {bar}")
    
    return temps, humidities, timestamps


if __name__ == "__main__":
    import sys
    
    filename = sys.argv[1] if len(sys.argv) > 1 else "sensor_data.csv"
    analyze_data(filename)
