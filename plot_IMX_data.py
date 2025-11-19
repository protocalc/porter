#!/usr/bin/env python3
"""
Plot IMX5 sensor data from CSV files.
Generates plots for IMU, INL2, and INS data and saves them to imx_data_plots/ directory.
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import pandas as pd


def plot_imu_data(imu_file, output_dir):
    """
    Plot IMU data: pqr (angular rates) and accelerations.
    
    Parameters:
    -----------
    imu_file : str or Path
        Path to IMU CSV file
    output_dir : str or Path
        Directory to save plots
    """
    print(f"Reading IMU data from {imu_file}...")
    df = pd.read_csv(imu_file)
    
    # Convert time to relative seconds from start
    time_s = (df['monotonic_ns'] - df['monotonic_ns'].iloc[0]) / 1e9
    
    # Plot PQR (angular rates)
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    axes[0].plot(time_s, df['pqr_P_rad_s'], 'b-', linewidth=0.8, label='P (Roll Rate)')
    axes[0].set_ylabel('P (rad/s)', fontsize=11)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    axes[0].set_title('IMU Angular Rates (PQR)', fontsize=12, fontweight='bold')
    
    axes[1].plot(time_s, df['pqr_Q_rad_s'], 'g-', linewidth=0.8, label='Q (Pitch Rate)')
    axes[1].set_ylabel('Q (rad/s)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=10)
    
    axes[2].plot(time_s, df['pqr_R_rad_s'], 'r-', linewidth=0.8, label='R (Yaw Rate)')
    axes[2].set_ylabel('R (rad/s)', fontsize=11)
    axes[2].set_xlabel('Time (s)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(fontsize=10)
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'imu_pqr.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()
    
    # Plot Accelerations
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    axes[0].plot(time_s, df['acc_X_m_s2'], 'b-', linewidth=0.8, label='X')
    axes[0].set_ylabel('X (m/s²)', fontsize=11)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    axes[0].set_title('IMU Accelerations (XYZ)', fontsize=12, fontweight='bold')
    
    axes[1].plot(time_s, df['acc_Y_m_s2'], 'g-', linewidth=0.8, label='Y')
    axes[1].set_ylabel('Y (m/s²)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=10)
    
    axes[2].plot(time_s, df['acc_Z_m_s2'], 'r-', linewidth=0.8, label='Z')
    axes[2].set_ylabel('Z (m/s²)', fontsize=11)
    axes[2].set_xlabel('Time (s)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(fontsize=10)
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'imu_acc_xyz.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()


def plot_inl2_data(inl2_file, output_dir):
    """
    Plot INL2 data: bias values for pqr and accelerations.
    
    Parameters:
    -----------
    inl2_file : str or Path
        Path to INL2 CSV file
    output_dir : str or Path
        Directory to save plots
    """
    print(f"Reading INL2 data from {inl2_file}...")
    df = pd.read_csv(inl2_file)
    
    # Convert time to relative seconds from start
    time_s = (df['monotonic_ns'] - df['monotonic_ns'].iloc[0]) / 1e9
    
    # Plot Bias PQR
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    axes[0].plot(time_s, df['biasPqr_x_rad_s'], 'b-', linewidth=0.8, label='Bias P')
    axes[0].set_ylabel('Bias P (rad/s)', fontsize=11)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    axes[0].set_title('INL2 Gyro Bias (PQR)', fontsize=12, fontweight='bold')
    
    axes[1].plot(time_s, df['biasPqr_y_rad_s'], 'g-', linewidth=0.8, label='Bias Q')
    axes[1].set_ylabel('Bias Q (rad/s)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=10)
    
    axes[2].plot(time_s, df['biasPqr_z_rad_s'], 'r-', linewidth=0.8, label='Bias R')
    axes[2].set_ylabel('Bias R (rad/s)', fontsize=11)
    axes[2].set_xlabel('Time (s)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(fontsize=10)
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'inl2_bias_pqr.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()
    
    # Plot Bias Accelerations
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    axes[0].plot(time_s, df['biasAcc_x_m_s2'], 'b-', linewidth=0.8, label='Bias X')
    axes[0].set_ylabel('Bias X (m/s²)', fontsize=11)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    axes[0].set_title('INL2 Accelerometer Bias (XYZ)', fontsize=12, fontweight='bold')
    
    axes[1].plot(time_s, df['biasAcc_y_m_s2'], 'g-', linewidth=0.8, label='Bias Y')
    axes[1].set_ylabel('Bias Y (m/s²)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=10)
    
    axes[2].plot(time_s, df['biasAcc_z_m_s2'], 'r-', linewidth=0.8, label='Bias Z')
    axes[2].set_ylabel('Bias Z (m/s²)', fontsize=11)
    axes[2].set_xlabel('Time (s)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(fontsize=10)
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'inl2_biasacc_xyz.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()


def plot_ins_data(ins_file, output_dir):
    """
    Plot INS data: altitude, attitude (roll/pitch/yaw), and velocities.
    
    Parameters:
    -----------
    ins_file : str or Path
        Path to INS CSV file
    output_dir : str or Path
        Directory to save plots
    """
    print(f"Reading INS data from {ins_file}...")
    df = pd.read_csv(ins_file)
    
    # Convert time to relative seconds from start
    time_s = (df['monotonic_ns'] - df['monotonic_ns'].iloc[0]) / 1e9
    
    # Convert radians to degrees for better readability
    roll_deg = np.rad2deg(df['roll_rad'])
    pitch_deg = np.rad2deg(df['pitch_rad'])
    yaw_deg = np.rad2deg(df['yaw_rad'])
    
    # Plot Altitude
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(time_s, df['alt_m'], 'b-', linewidth=0.8, label='Altitude')
    ax.set_ylabel('Altitude (m)', fontsize=11)
    ax.set_xlabel('Time (s)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    ax.set_title('INS Altitude', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'ins_altitude.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()
    
    # Plot Roll, Pitch, Yaw
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    axes[0].plot(time_s, roll_deg, 'b-', linewidth=0.8, label='Roll')
    axes[0].set_ylabel('Roll (deg)', fontsize=11)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    axes[0].set_title('INS Attitude (Roll/Pitch/Yaw)', fontsize=12, fontweight='bold')
    
    axes[1].plot(time_s, pitch_deg, 'g-', linewidth=0.8, label='Pitch')
    axes[1].set_ylabel('Pitch (deg)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=10)
    
    axes[2].plot(time_s, yaw_deg, 'r-', linewidth=0.8, label='Yaw')
    axes[2].set_ylabel('Yaw (deg)', fontsize=11)
    axes[2].set_xlabel('Time (s)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(fontsize=10)
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'ins_roll_pitch_yaw.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()
    
    # Plot Velocities U, V, W
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    axes[0].plot(time_s, df['vel_U_m_s'], 'b-', linewidth=0.8, label='U (Forward)')
    axes[0].set_ylabel('U (m/s)', fontsize=11)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    axes[0].set_title('INS Velocities (UVW)', fontsize=12, fontweight='bold')
    
    axes[1].plot(time_s, df['vel_V_m_s'], 'g-', linewidth=0.8, label='V (Right)')
    axes[1].set_ylabel('V (m/s)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=10)
    
    axes[2].plot(time_s, df['vel_W_m_s'], 'r-', linewidth=0.8, label='W (Down)')
    axes[2].set_ylabel('W (m/s)', fontsize=11)
    axes[2].set_xlabel('Time (s)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(fontsize=10)
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'ins_vel_uvw.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Plot IMX5 sensor data from CSV files')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Directory containing IMX5 CSV files (default: data)')
    parser.add_argument('--output-dir', type=str, default='imx_data_plots',
                        help='Directory to save plots (default: imx_data_plots)')
    parser.add_argument('--prefix', type=str, default='IMX5-Sensors',
                        help='Prefix of CSV files to process (default: IMX5-Sensors)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Find all matching CSV files in the data directory
    data_dir = Path(args.data_dir)
    imu_files = sorted(data_dir.glob(f'{args.prefix}*_imu.csv'))
    inl2_files = sorted(data_dir.glob(f'{args.prefix}*_inl2.csv'))
    ins_files = sorted(data_dir.glob(f'{args.prefix}*_ins.csv'))
    
    if not imu_files and not inl2_files and not ins_files:
        print(f"No IMX5 CSV files found in {data_dir}")
        return
    
    # Process each set of files
    for imu_file in imu_files:
        print(f"\n{'='*60}")
        print(f"Processing IMU file: {imu_file.name}")
        print('='*60)
        try:
            plot_imu_data(imu_file, output_dir)
        except Exception as e:
            print(f"  Error processing IMU file: {e}")
    
    for inl2_file in inl2_files:
        print(f"\n{'='*60}")
        print(f"Processing INL2 file: {inl2_file.name}")
        print('='*60)
        try:
            plot_inl2_data(inl2_file, output_dir)
        except Exception as e:
            print(f"  Error processing INL2 file: {e}")
    
    for ins_file in ins_files:
        print(f"\n{'='*60}")
        print(f"Processing INS file: {ins_file.name}")
        print('='*60)
        try:
            plot_ins_data(ins_file, output_dir)
        except Exception as e:
            print(f"  Error processing INS file: {e}")
    
    print(f"\n{'='*60}")
    print(f"All plots saved to: {output_dir}")
    print('='*60)


if __name__ == '__main__':
    main()
