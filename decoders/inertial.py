import argparse
import os
import struct

import numpy as np
from io import StringIO
import matplotlib.pyplot as plt

def main():

    parser = argparse.ArgumentParser(description="Plot data from the inertial sensors.")

    parser.add_argument("path", type=str, help="Path to the inertial folder with sensor files.")
    
    args = parser.parse_args()
    print(args)

    string = args.path.split("/")
    filepath = "/".join(string[:-1])
    accel_path = filepath + "/accelerometer.bin"
    gyro_path = filepath + "/gyroscope.bin"
    bar_path = filepath + "/barometer.bin"
    mag_path = filepath + "/magnetometer.bin"

    if not os.path.exists(filepath + "/plots"):
        os.mkdir(filepath + "/plots")

    with open(accel_path, "r") as f:
        accel_lines = f.readlines()
    with open(gyro_path, "r") as f:
        gyro_lines = f.readlines()
    with open(bar_path, "r") as f:
        bar_lines = f.readlines()
    with open(mag_path, "r") as f:
        mag_lines = f.readlines()

    accel_lines = accel_lines[:-1]
    gyro_lines = gyro_lines[:-1]
    bar_lines = bar_lines[:-1]
    mag_lines = mag_lines[:-1]

    accel_data = np.loadtxt(StringIO("".join(accel_lines)), delimiter=" ")
    gyro_data = np.loadtxt(StringIO("".join(gyro_lines)), delimiter=" ")
    bar_data = np.loadtxt(StringIO("".join(bar_lines)), delimiter=" ")
    mag_data = np.loadtxt(StringIO("".join(mag_lines)), delimiter=" ")

    print("All data loaded successfully")

    titles = ["Accelerometer", "Gyroscope", "Magnetometer"]
    ylabels = ["Acceleration [g]", "Angular Velocity [rad/s]", "Magnetic Field [uT]"]
    labels = ["Acceleration X", "Acceleration Y", "Acceleration Z", "Angular Velocity X", "Angular Velocity Y", "Angular Velocity Z", "Magnetic Field X", "Magnetic Field Y", "Magnetic Field Z"]
    data_list = [accel_data, gyro_data, mag_data]
    colors = ['blue', 'red', 'green']

    for idx, data in enumerate(data_list):
        timestamps = data[:, 0] - data[0, 0]
        timing = []
        x = data[:, 1]
        y = data[:, 2]
        z = data[:, 3]

        outpath_timing = filepath + "/plots/" + titles[idx].lower() + "_timing.png"
        outpath_data = filepath + "/plots/" + titles[idx].lower() + "_data.png"
        
        test_duration = (timestamps[-1] - timestamps[0]) / (1e6)
        
        for i in range(0, len(timestamps)-1):
            timing.append(timestamps[i+1] - timestamps[i])

        plt.figure()
        y_printouts, x_printouts, _ = plt.hist(timing, bins=100, edgecolor="black", color=colors[idx])
        plt.title(f"{titles[idx]} Timing Results")
        plt.xlabel(f"{titles[idx]} time between reads (us)")
        plt.text(0.3 * (np.max(x_printouts)-np.min(x_printouts)) + np.min(x_printouts), 0.9 * np.max(y_printouts), f'Maximum: {np.round(np.max(timing), 3)} us', fontsize=12)
        plt.text(0.3 * (np.max(x_printouts)-np.min(x_printouts)) + np.min(x_printouts), 0.85 * np.max(y_printouts), f'Mean: {np.round(np.mean(timing), 3)} us', fontsize=12)
        plt.text(0.3 * (np.max(x_printouts)-np.min(x_printouts)) + np.min(x_printouts), 0.8 * np.max(y_printouts), f'St. Dev.: {np.round(np.std(timing), 3)} us', fontsize=12)
        plt.text(0.3 * (np.max(x_printouts)-np.min(x_printouts)) + np.min(x_printouts), 0.75 * np.max(y_printouts), f'Total Readouts: {len(timing)}', fontsize=12)
        plt.text(0.3 * (np.max(x_printouts)-np.min(x_printouts)) + np.min(x_printouts), 0.7 * np.max(y_printouts), f'Readout Frequency: {np.round(len(timing) / test_duration, 3)} Hz', fontsize=12)
        plt.savefig(outpath_timing, format="png")
        plt.show()

        plt.figure()
        plt.plot(timestamps, x, color='blue', label=labels[(3*idx)])
        plt.plot(timestamps, y, color='red', label=labels[(3*idx + 1)])
        plt.plot(timestamps, z, color='green', label=labels[(3*idx + 2)])
        plt.title(f"{titles[idx]} Readings")
        plt.xlabel("Time (us)")
        plt.ylabel(f"{ylabels[idx]}")
        plt.legend()
        plt.savefig(outpath_data, format="png")
        plt.show()

        print(f"{titles[idx]} plots saved")

    # Barometer has a separate structure
    bar_timestamps = bar_data[:, 0] - bar_data[0, 0]
    bar_timing = []
    bar_pressure = bar_data[:, 1]
    bar_temp = bar_data[:, 2]

    for i in range(0, len(bar_timestamps)-1):
        bar_timing.append(bar_timestamps[i+1] - bar_timestamps[i])

    bar_timing_outpath = filepath + "/plots/barometer_timing.png"
    bar_temp_outpath = filepath + "/plots/barometer_temp.png"
    bar_pres_outpath = filepath + "/plots/barometer_pres.png"

    test_duration = (bar_timestamps[-1] - bar_timestamps[0]) / (1e6)

    plt.figure()
    y_printouts, x_printouts, _ = plt.hist(bar_timing, bins=100, edgecolor="black", color='yellow')
    plt.title(f"Barometer Timing Results")
    plt.xlabel(f"Barometer time between reads (us)")
    plt.text(0.3 * (np.max(x_printouts)-np.min(x_printouts))+ np.min(x_printouts), 0.9 * np.max(y_printouts), f'Maximum: {np.round(np.max(bar_timing), 3)} us', fontsize=12)
    plt.text(0.3 * (np.max(x_printouts)-np.min(x_printouts)) + np.min(x_printouts), 0.85 * np.max(y_printouts), f'Mean: {np.round(np.mean(bar_timing), 3)} us', fontsize=12)
    plt.text(0.3 * (np.max(x_printouts)-np.min(x_printouts)) + np.min(x_printouts), 0.8 * np.max(y_printouts), f'St. Dev.: {np.round(np.std(bar_timing), 3)} us', fontsize=12)
    plt.text(0.3 * (np.max(x_printouts)-np.min(x_printouts)) + np.min(x_printouts), 0.75 * np.max(y_printouts), f'Total Readouts: {len(bar_timing)}', fontsize=12)
    plt.text(0.3 * (np.max(x_printouts)-np.min(x_printouts)) + np.min(x_printouts), 0.7 * np.max(y_printouts), f'Readout Frequency: {np.round(len(bar_timing) / test_duration, 3)} Hz', fontsize=12)
    plt.savefig(bar_timing_outpath, format="png")
    plt.show()

    plt.figure()
    plt.plot(bar_timestamps, bar_pressure, color='blue')
    plt.title(f"Barometer Pressure Readings")
    plt.xlabel("Time (us)")
    plt.ylabel(f"Pressure [Pa]")
    plt.savefig(bar_pres_outpath, format="png")
    plt.show()

    plt.figure()
    plt.plot(bar_timestamps, bar_temp, color='red')
    plt.title(f"Barometer Temperature Readings")
    plt.xlabel("Time (us)")
    plt.ylabel(f"Temperature [C]")
    plt.savefig(bar_temp_outpath, format="png")
    plt.show()

    print("All plots saved")


if __name__ == "__main__":
    main()

