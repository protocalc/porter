import argparse
import os
import struct

import numpy as np


def main():

    parser = argparse.ArgumentParser(description="Decode data from the ADC.")

    parser.add_argument("path", type=str, help="Path with the data to be decoded")

    parser.add_argument(
        "--voltage",
        default=False,
        help="Flag to indicate that the ADC data are saved as voltage",
    )

    parser.add_argument(
        "--plot",
        default=False,
        help="Flag to plot the data",
    )

    args = parser.parse_args()
    print(args)

    filepath = args.path.split("ADS")[0]
    print(filepath)
    string = "ADS" + args.path.split("ADS")[-1].split('.bin')[0]
    print(string)

    if not os.path.exists(filepath + "/decoded"):
        os.mkdir(filepath + "/decoded")

    if args.voltage:
        pattern = "dqf"
    else:
        pattern = "di"


    '''
    with open(args.path, "rb") as fstream:
        data = fstream.read()

    reps = int(len(data) / 20)

    expected_size = struct.calcsize("<" + pattern * reps)
    actual_size = len(data)

    print(expected_size,actual_size)

    if actual_size < expected_size:
        print(f"Data size mismatch! Expected {expected_size} bytes, got {actual_size} bytes.")
    else:
        vals = struct.unpack("<dqf" + pattern * reps, data)

    final = np.reshape(np.array(vals), (reps, 3))'
    '''

    decoded_filename = filepath + "/decoded/" + string + ".txt"

    print(decoded_filename)

    abs_time_vec = [] 
    rel_time_vec = []
    sensor_value_vec = []

    with open(args.path, "rb") as f:
        while chunk := f.read(20):  # Read 20 bytes per sample
            if len(chunk) != 20:
                print("Incomplete sample, skipping...")
                continue
            
            # Unpack using the same format as packing
            abs_time, rel_time, sensor_value = struct.unpack("<dqf", chunk)

            abs_time_vec.append(abs_time)
            rel_time_vec.append(rel_time)
            sensor_value_vec.append(sensor_value)

    final = np.array([abs_time_vec,rel_time_vec,sensor_value_vec]).T

    if args.plot:
        import matplotlib.pyplot as plt

        plt.plot(final[:, 0] - final[0, 0], final[:, 2])
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.show()
        plt.hist(final[:, 1]/1e9, bins=10)
        plt.hist(np.diff(final[:, 0] - final[0, 0]), bins=10)
        plt.show()
        
        print(f'Mean Reading Time: {np.mean(final[:, 1]/1e9)}')
        print(f'Mean Time Samples: {np.mean(np.diff(final[:, 0] - final[0, 0]))}')

    # save_data = open(decoded_filename,'w')
    # for abs_t,rel_t,data in zip(abs_time_vec,rel_time_vec,sensor_value_vec):
    #     save_data.write(f'{abs_t}           {rel_t}         {data}      \n')
    # save_data.close()

if __name__ == "__main__":
    main()
