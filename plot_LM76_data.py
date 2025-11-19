#!/usr/bin/env python3
"""
Plot LM76 temperature sensor data from CSV files.
Reads timestamp and temperature values and generates plots.
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import pandas as pd


def plot_lm76_data(lm76_file, output_dir):
    """
    Plot LM76 temperature data over time.
    
    Parameters:
    -----------
    lm76_file : str or Path
        Path to LM76 CSV file
    output_dir : str or Path
        Directory to save plots
    """
    print(f"Reading LM76 data from {lm76_file}...")
    df = pd.read_csv(lm76_file)
    
    if len(df) == 0:
        print("  No data found in file")
        return
    
    # Convert monotonic time to relative seconds from start
    time_s = (df['monotonic_ns'] - df['monotonic_ns'].iloc[0]) / 1e9
    
    # Get temperature data
    temp_c = df['temperature_c']
    
    # Calculate statistics
    mean_temp = np.mean(temp_c)
    std_temp = np.std(temp_c)
    min_temp = np.min(temp_c)
    max_temp = np.max(temp_c)
    
    print(f"  Total samples: {len(df)}")
    print(f"  Duration: {time_s.iloc[-1]:.2f} seconds")
    print(f"  Temperature - Mean: {mean_temp:.4f} °C, Std: {std_temp:.4f} °C")
    print(f"  Temperature - Min: {min_temp:.4f} °C, Max: {max_temp:.4f} °C")
    
    # Create single plot with temperature over time
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(time_s, temp_c, 'b-', linewidth=0.8, alpha=0.7, label='Temperature')
    ax.axhline(mean_temp, color='red', linestyle='--', linewidth=1.5, 
               label=f'Mean: {mean_temp:.4f} °C')
    
    ax.set_xlabel('Time (s)', fontsize=11)
    ax.set_ylabel('Temperature (°C)', fontsize=11)
    ax.set_title('LM76 Temperature Sensor Data', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    # Add statistics text box
    stats_text = f'Samples: {len(df)}\n'
    stats_text += f'Duration: {time_s.iloc[-1]:.2f} s\n'
    stats_text += f'Mean: {mean_temp:.4f} °C\n'
    stats_text += f'Std: {std_temp:.4f} °C\n'
    stats_text += f'Min: {min_temp:.4f} °C\n'
    stats_text += f'Max: {max_temp:.4f} °C'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save the plot
    output_path = Path(output_dir) / 'lm76_temperature.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Plot LM76 temperature sensor data from CSV files')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Directory containing LM76 CSV files (default: data)')
    parser.add_argument('--output-dir', type=str, default='lm76_data_plots',
                        help='Directory to save plots (default: lm76_data_plots)')
    parser.add_argument('--prefix', type=str, default='LM76-Temp',
                        help='Prefix of CSV files to process (default: LM76-Temp)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Find all matching CSV files in the data directory
    data_dir = Path(args.data_dir)
    lm76_files = sorted(data_dir.glob(f'{args.prefix}*.csv'))
    
    if not lm76_files:
        print(f"No LM76 CSV files found in {data_dir}")
        return
    
    # Process each file
    for lm76_file in lm76_files:
        print(f"\n{'='*60}")
        print(f"Processing LM76 file: {lm76_file.name}")
        print('='*60)
        try:
            plot_lm76_data(lm76_file, output_dir)
        except Exception as e:
            print(f"  Error processing LM76 file: {e}")
    
    print(f"\n{'='*60}")
    print(f"All plots saved to: {output_dir}")
    print('='*60)


if __name__ == '__main__':
    main()
