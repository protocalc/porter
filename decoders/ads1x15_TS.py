import argparse
import os
import struct
import pandas as pd
import numpy as np


def main():

    parser = argparse.ArgumentParser(description="Decode data from the ADC.")

    parser.add_argument("path", type=str, help="Path with the data to be decoded")

    # parser.add_argument(
    #     "--voltage",
    #     default=True,
    #     help="Flag to indicate that the ADC data are saved as voltage",
    # )

    parser.add_argument("-p", "--plot", action="store_true",
        help="Flag to plot the data",
    )

    args = parser.parse_args()
    print(args)

    string = args.path.split("/")

    filepath = "/".join(string[:-1])

    if not os.path.exists(filepath + "/decoded"):
        os.mkdir(filepath + "/decoded")

    pattern = "dqf"

    with open(args.path, "rb") as fstream:
        data = fstream.read()

    abs_time_vec = [] 
    rel_time_vec = []
    sensor_value_vec = []
    with open(args.path, "rb") as f:
        while chunk := f.read(20):  # Read 20 bytes per sample
                if len(chunk) != 20:
                    print("Incomplete sample, skipping...")
                    continue
                abs_time, rel_time, sensor_value = struct.unpack("<dqf", chunk)

                abs_time_vec.append(abs_time)
                rel_time_vec.append(rel_time)
                sensor_value_vec.append(sensor_value)
        
    # reps = int(len(data)/20)
    # vals = struct.unpack("<" + pattern * reps, data)
    # vals = np.reshape(np.array(vals), (reps, 3))
    adc_data = pd.DataFrame(np.array([abs_time_vec, rel_time_vec, sensor_value_vec]).T, columns=["time", "reading_time", "amplitude"])
    adc_data = adc_data.sort_values("time")
    #adc_data.to_csv(os.path.join(os.path.split(args.path)[0], "decoded/ads.csv"))

    # adc_data["reading_time"] = adc_data["reading_time"].values.argsort(adc_data['time'])
    # adc_data["amplitude"] = adc_data["amplitude"].values.argsort(adc_data['time'])
    # adc_data['time'] = adc_data["time"].values.sort()

    
    if args.plot:
        import matplotlib.pyplot as plt

        plt.plot(adc_data["time"], adc_data["amplitude"])
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.show()
        plt.hist(adc_data["reading_time"]/1e9, bins=10)
        plt.hist(np.diff(adc_data["reading_time"]), bins=10)
        plt.show()
        
        print(f'Mean Reading Time: {np.mean(adc_data["reading_time"]/1e9)}')
        print(f'Mean Time Samples: {np.mean(np.diff(adc_data["reading_time"] - adc_data["reading_time"][0]))}')

    
    


if __name__ == "__main__":
    main()