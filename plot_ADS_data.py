#!/usr/bin/env python3
"""
Plot ADS1015 ADC data from binary files.
Reads timestamp and ADC values, converts to voltage, and generates plots.
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path

# Gain values for ADS1015
ADS1015_VALUE_GAIN = {
    1: 4.096,
    2: 2.048,
    4: 1.024,
    8: 0.512,
    16: 0.256,
}


def read_ads_file(filepath):
    """
    Read ADS1015 binary file (text format with timestamp and value).
    
    Parameters:
    -----------
    filepath : str or Path
        Path to ADS1015 .bin file
        
    Returns:
    --------
    timestamps : array
        Timestamps in nanoseconds
    values : array
        Raw ADC values
    """
    timestamps = []
    values = []
    
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    timestamp_ns = int(parts[0])
                    value = int(parts[1])
                    timestamps.append(timestamp_ns)
                    values.append(value)
                except (ValueError, IndexError):
                    continue
    
    return np.array(timestamps), np.array(values)


def convert_to_voltage(values, gain=8):
    """
    Convert raw ADC values to voltage.
    
    Parameters:
    -----------
    values : array
        Raw ADC values (12-bit signed integer)
    gain : int
        Gain setting (1, 2, 4, 8, or 16)
        
    Returns:
    --------
    voltages : array
        Voltage values
    """
    gain_value = ADS1015_VALUE_GAIN.get(gain, 0.512)
    # ADS1015 is 12-bit, so max value is 2047 (signed)
    voltages = values * gain_value / 2048.0
    return voltages


def plot_ads_data(ads_file, output_dir, gain=8):
    """
    Plot ADS1015 data: raw values and converted voltage over time.
    
    Parameters:
    -----------
    ads_file : str or Path
        Path to ADS1015 .bin file
    output_dir : str or Path
        Directory to save plots
    gain : int
        Gain setting used during data collection
    """
    print(f"Reading ADS1015 data from {ads_file}...")
    timestamps, values = read_ads_file(ads_file)
    
    if len(timestamps) == 0:
        print("  No data found in file")
        return
    
    # Convert timestamps_us to relative seconds from start
    time_s = (timestamps - timestamps[0]) / 1e6
    
    # Convert to voltage
    voltages = convert_to_voltage(values, gain)
    
    # Calculate statistics
    mean_voltage = np.mean(voltages)
    std_voltage = np.std(voltages)
    min_voltage = np.min(voltages)
    max_voltage = np.max(voltages)
    
    print(f"  Total samples: {len(timestamps)}")
    print(f"  Duration: {time_s[-1]:.2f} seconds")
    print(f"  Voltage - Mean: {mean_voltage:.4f} V, Std: {std_voltage:.4f} V")
    print(f"  Voltage - Min: {min_voltage:.4f} V, Max: {max_voltage:.4f} V")
    
    # Create single plot with voltage over time
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(time_s, voltages, 'b-', linewidth=0.5, alpha=0.7, label='Voltage')
    ax.axhline(mean_voltage, color='red', linestyle='--', linewidth=1.5, 
               label=f'Mean: {mean_voltage:.4f} V')
    
    ax.set_xlabel('Time (s)', fontsize=11)
    ax.set_ylabel('Voltage (V)', fontsize=11)
    ax.set_title(f'ADS1015 ADC Data (Gain={gain}, Range=±{ADS1015_VALUE_GAIN[gain]} V)', 
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    # Add statistics text box
    stats_text = f'Samples: {len(timestamps)}\n'
    stats_text += f'Duration: {time_s[-1]:.2f} s\n'
    stats_text += f'Mean: {mean_voltage:.4f} V\n'
    stats_text += f'Std: {std_voltage:.4f} V\n'
    stats_text += f'Min: {min_voltage:.4f} V\n'
    stats_text += f'Max: {max_voltage:.4f} V'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.xlim(100, 100.5) 
    
    # Save the plot
    output_path = Path(output_dir) / 'ads1015_voltage.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Plot ADS1015 ADC data from binary files')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Directory containing ADS1015 .bin files (default: data)')
    parser.add_argument('--output-dir', type=str, default='ads_data_plots',
                        help='Directory to save plots (default: ads_data_plots)')
    parser.add_argument('--gain', type=int, default=8, choices=[1, 2, 4, 8, 16],
                        help='Gain setting used during data collection (default: 8)')
    parser.add_argument('--prefix', type=str, default='ADS1015',
                        help='Prefix of .bin files to process (default: ADS1015)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Find all matching .bin files in the data directory
    data_dir = Path(args.data_dir)
    ads_files = sorted(data_dir.glob(f'{args.prefix}*.bin'))
    
    if not ads_files:
        print(f"No ADS1015 .bin files found in {data_dir}")
        return
    
    # Process each file
    for ads_file in ads_files:
        print(f"\n{'='*60}")
        print(f"Processing ADS1015 file: {ads_file.name}")
        print('='*60)
        try:
            plot_ads_data(ads_file, output_dir, args.gain)
        except Exception as e:
            print(f"  Error processing ADS1015 file: {e}")
    
    print(f"\n{'='*60}")
    print(f"All plots saved to: {output_dir}")
    print('='*60)


if __name__ == '__main__':
    main()
