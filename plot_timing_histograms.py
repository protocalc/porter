#!/usr/bin/env python3
"""
Plot timing histograms for sensor data files.
Shows timing intervals between consecutive samples for IMU, INS, and binary sensor data.
"""

import struct
import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path


def remove_outliers(intervals_ms, method='iqr', threshold=3.0):
    """
    Remove outliers from timing intervals.
    
    Parameters:
    -----------
    intervals_ms : array
        Timing intervals in milliseconds
    method : str
        Method for outlier detection: 'iqr' (Interquartile Range) or 'zscore'
    threshold : float
        For IQR: multiplier for IQR (default 3.0 for more aggressive filtering)
        For zscore: number of standard deviations (default 3.0)
        
    Returns:
    --------
    filtered : array
        Intervals with outliers removed
    num_removed : int
        Number of outliers removed
    """
    if method == 'iqr':
        q1 = np.percentile(intervals_ms, 25)
        q3 = np.percentile(intervals_ms, 75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        mask = (intervals_ms >= lower_bound) & (intervals_ms <= upper_bound)
    elif method == 'zscore':
        mean = np.mean(intervals_ms)
        std = np.std(intervals_ms)
        z_scores = np.abs((intervals_ms - mean) / std)
        mask = z_scores < threshold
    else:
        raise ValueError(f"Unknown method: {method}")
    
    filtered = intervals_ms[mask]
    num_removed = len(intervals_ms) - len(filtered)
    
    return filtered, num_removed


def plot_timing_histogram(intervals_ms, dataset_name, output_path=None):
    """
    Plot timing histogram with mean, std, and frequency in title.
    
    Parameters:
    -----------
    intervals_ms : array
        Timing intervals in milliseconds
    dataset_name : str
        Name of the dataset for labeling
    output_path : str, optional
        Path to save the figure
    """
    mean_ms = np.mean(intervals_ms)
    std_ms = np.std(intervals_ms)
    freq_hz = 1000.0 / mean_ms  # Convert ms to Hz
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot histogram
    n, bins, patches = ax.hist(intervals_ms, bins=50, color='#4472C4', edgecolor='black', alpha=0.9)
    
    # Add mean line
    ax.axvline(mean_ms, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_ms:.2f} ms')
    
    # Set title with stats
    ax.set_title(f'Timing Intervals Histogram (Mean: {mean_ms:.2f} ms, Std: {std_ms:.4f} ms, Freq: {freq_hz:.1f} Hz)',
                 fontsize=12, fontweight='bold')
    
    # Labels
    ax.set_xlabel('Interval (ms)', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    
    # Legend
    ax.legend(fontsize=10)
    
    # Grid
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save or show
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()
    
    plt.close()


def process_csv_file(filepath, remove_outliers_flag=False):
    """
    Process CSV file and extract timestamps.
    
    Parameters:
    -----------
    filepath : str or Path
        Path to the CSV file
    remove_outliers_flag : bool
        Whether to apply outlier rejection (for IMU/INS data)
        
    Returns:
    --------
    intervals_ms : array
        Timing intervals in milliseconds
    """
    timestamps = []
    
    with open(filepath, 'r') as f:
        # Skip header
        next(f)
        
        for line in f:
            parts = line.strip().split(',')
            if parts:
                try:
                    # Timestamp is in nanoseconds in first column
                    timestamp_ns = int(parts[0])
                    timestamps.append(timestamp_ns)
                except (ValueError, IndexError):
                    continue
    
    timestamps = np.array(timestamps)
    
    # Calculate intervals in milliseconds
    intervals_ns = np.diff(timestamps)
    intervals_ms = intervals_ns / 1e6
    
    # Apply outlier rejection if requested
    if remove_outliers_flag:
        filtered, num_removed = remove_outliers(intervals_ms, method='iqr', threshold=3.0)
        if num_removed > 0:
            print(f"  Removed {num_removed} outliers ({100*num_removed/len(intervals_ms):.2f}%)")
        intervals_ms = filtered
    
    return intervals_ms


def process_text_file(filepath):
    """
    Process text file (space-separated) and extract timestamps.
    
    Parameters:
    -----------
    filepath : str or Path
        Path to the text file
        
    Returns:
    --------
    intervals_ms : array or None
        Timing intervals in milliseconds, or None if file is empty
    """
    filepath = Path(filepath)
    
    # Check if file is empty
    if filepath.stat().st_size == 0:
        print(f"Warning: {filepath.name} is empty (0 bytes)")
        return None
    
    timestamps = []
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    try:
                        # First column is timestamp in microseconds
                        timestamp_us = int(parts[0])
                        timestamps.append(timestamp_us)
                    except (ValueError, IndexError):
                        continue
    except UnicodeDecodeError:
        # If it's truly binary, return None
        print(f"Warning: {filepath.name} appears to be binary format (not yet supported)")
        return None
    
    if len(timestamps) < 2:
        print(f"Warning: {filepath.name} has insufficient data")
        return None
    
    timestamps = np.array(timestamps)
    
    # Calculate intervals in milliseconds
    intervals_us = np.diff(timestamps)
    intervals_ms = intervals_us / 1000.0
    
    return intervals_ms


def main():
    parser = argparse.ArgumentParser(
        description='Plot timing histograms for sensor data files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--data-dir',
        default='data/sensors_data',
        help='Directory containing sensor data files (default: data/sensors_data)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='timing_histograms',
        help='Directory to save histogram plots (default: timing_histograms)'
    )
    
    parser.add_argument(
        '--show',
        action='store_true',
        help='Display plots instead of saving them'
    )
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    if not data_dir.exists():
        print(f"Error: Data directory '{data_dir}' not found")
        return
    
    # Create output directory if saving
    if not args.show:
        output_dir.mkdir(exist_ok=True)
        print(f"Output directory: {output_dir}")
    
    print("\nProcessing sensor data files...")
    print("=" * 60)

    # Process LM76 CSV file
    lm76_files = list(data_dir.glob('LM76-Temp_*.csv'))
    if lm76_files:
        lm76_file = lm76_files[0]
        print(f"\nProcessing: {lm76_file.name}")
        intervals = process_csv_file(lm76_file, remove_outliers_flag=False)
        
        if intervals is not None and len(intervals) > 0:
            output_path = None if args.show else output_dir / 'lm76_timing_histogram.png'
            plot_timing_histogram(intervals, 'LM76', output_path)
            print(f"  Records: {len(intervals) + 1}")
            print(f"  Mean interval: {np.mean(intervals):.2f} ms ({1000/np.mean(intervals):.1f} Hz)")
            print(f"  Std: {np.std(intervals):.4f} ms")
    
    # Process IMU CSV file
    imu_files = list(data_dir.glob('*_imu.csv'))
    if imu_files:
        imu_file = imu_files[0]
        print(f"\nProcessing: {imu_file.name}")
        intervals = process_csv_file(imu_file, remove_outliers_flag=False)
        
        if intervals is not None and len(intervals) > 0:
            output_path = None if args.show else output_dir / 'imu_timing_histogram.png'
            plot_timing_histogram(intervals, 'IMU', output_path)
            print(f"  Records: {len(intervals) + 1}")
            print(f"  Mean interval: {np.mean(intervals):.2f} ms ({1000/np.mean(intervals):.1f} Hz)")
            print(f"  Std: {np.std(intervals):.4f} ms")
    
    # Process INS CSV file
    ins_files = list(data_dir.glob('*_ins.csv'))
    if ins_files:
        ins_file = ins_files[0]
        print(f"\nProcessing: {ins_file.name}")
        intervals = process_csv_file(ins_file, remove_outliers_flag=False)
        
        if intervals is not None and len(intervals) > 0:
            output_path = None if args.show else output_dir / 'ins_timing_histogram.png'
            plot_timing_histogram(intervals, 'INS', output_path)
            print(f"  Records: {len(intervals) + 1}")
            print(f"  Mean interval: {np.mean(intervals):.2f} ms ({1000/np.mean(intervals):.1f} Hz)")
            print(f"  Std: {np.std(intervals):.4f} ms")

    # Process INL2 CSV file
    inl2_files = list(data_dir.glob('*_inl2.csv'))
    if inl2_files:
        inl2_file = inl2_files[0]
        print(f"\nProcessing: {inl2_file.name}")
        intervals = process_csv_file(inl2_file, remove_outliers_flag=False)
        
        if intervals is not None and len(intervals) > 0:
            output_path = None if args.show else output_dir / 'inl2_timing_histogram.png'
            plot_timing_histogram(intervals, 'INL2', output_path)
            print(f"  Records: {len(intervals) + 1}")
            print(f"  Mean interval: {np.mean(intervals):.2f} ms ({1000/np.mean(intervals):.1f} Hz)")
            print(f"  Std: {np.std(intervals):.4f} ms")
    
    # Process ADS1015 (ADC) file
    ads_files = list(data_dir.glob('ADS*.bin'))
    if ads_files:
        ads_file = ads_files[0]
        print(f"\nProcessing: {ads_file.name}")
        intervals = process_text_file(ads_file)
        
        if intervals is not None and len(intervals) > 0:
            output_path = None if args.show else output_dir / 'ads_timing_histogram.png'
            plot_timing_histogram(intervals, 'ADS1015 (ADC)', output_path)
            print(f"  Records: {len(intervals) + 1}")
            print(f"  Mean interval: {np.mean(intervals):.2f} ms ({1000/np.mean(intervals):.1f} Hz)")
            print(f"  Std: {np.std(intervals):.4f} ms")
    
    # Process text/binary files in Inertial directory
    inertial_dirs = list(data_dir.glob('Inertial_*.bin'))
    if inertial_dirs:
        inertial_dir = inertial_dirs[0]
        print(f"\nProcessing sensor files in: {inertial_dir.name}")
        
        # Define sensor files (these are text files with space-separated values)
        sensor_files = {
            'barometer.bin': 'Barometer',
            'magnetometer.bin': 'Magnetometer',
            'accelerometer.bin': 'Accelerometer',
            'gyroscope.bin': 'Gyroscope',
        }
        
        for filename, label in sensor_files.items():
            filepath = inertial_dir / filename
            
            if filepath.exists():
                print(f"\nProcessing: {filename}")
                intervals = process_text_file(filepath)
                
                if intervals is not None and len(intervals) > 0:
                    output_path = None if args.show else output_dir / f'{label.lower()}_timing_histogram.png'
                    plot_timing_histogram(intervals, label, output_path)
                    print(f"  Records: {len(intervals) + 1}")
                    print(f"  Mean interval: {np.mean(intervals):.2f} ms ({1000/np.mean(intervals):.1f} Hz)")
                    print(f"  Std: {np.std(intervals):.2f} ms")
    
    print("\n" + "=" * 60)
    print("Processing complete!")
    
    if not args.show:
        print(f"\nHistograms saved to: {output_dir}/")


if __name__ == '__main__':
    main()
