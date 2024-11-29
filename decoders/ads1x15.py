import argparse
import os
import struct

import numpy as np


def convert_to_readings(values):

    readings = np.zeros(len(values))

    for i in range(len(values)):

        raw_value = ((values[i][0] << 8) | values[i][1]) >> 4
        if raw_value > 2047:
            raw_value -= 4096

        readings[i] = raw_value

    return readings


def main():

    parser = argparse.ArgumentParser(description="Decode data from the ADC.")

    parser.add_argument("path", type=str, help="Path with the data to be decoded")

    parser.add_argument(
        "--voltage",
        default=False,
        help="Flag to indicate that the ADC data are saved as voltage",
    )

    parser.add_argument(
        "--gain",
        default=0.256,
        help="Gain of the ADC to convert to voltage",
    )

    parser.add_argument(
        "--plot",
        default=False,
        help="Flag to plot the data",
    )

    args = parser.parse_args()

    string = args.path.split("/")

    filepath = "/".join(string[:-1])

    if not os.path.exists(filepath + "/decoded"):
        os.mkdir(filepath + "/decoded")

    if args.voltage:
        pattern = "dqf"
    else:
        pattern = "di"

    with open(args.path, "rb") as fstream:
        data = fstream.read()

    reps = int(len(data) / 18)

    dtype = np.dtype([("time", "S8"), ("read_time", "S8"), ("raw_value", "S2")])
    array = np.frombuffer(msg_buffer, dtype=dtype)

    final = np.zeros((reps, 4))

    final[:, 0] = struct.unpack("<d" * reps, array["time"])
    final[:, 1] = struct.unpack("<q" * reps, array["read_time"])
    final[:, 2] = final[:, 0] - final[:, 1] / 1e9 / 2

    readings = convert_to_readings(array["raw_value"])

    if args.voltage:
        final[:, 3] = (readings * gain) / 4096.0
    else:
        final[:, 3] = readings

    decoded_filename = filepath + "/decoded/" + string[-1][:-4] + ".csv"

    if args.plot:
        import matplotlib.pyplot as plt

        plt.plot(final[:, 0] - final[0, 0], final[:, 3])
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.show()
        plt.hist(final[:, 1] / 1e9, bins=10)
        plt.hist(np.diff(final[:, 0] - final[0, 0]), bins=10)
        plt.show()

        print(f"Mean Reading Time: {np.mean(final[:, 1]/1e9)}")
        print(f"Mean Time Samples: {np.mean(np.diff(final[:, 0] - final[0, 0]))}")

    np.savetxt(decoded_filename, final)


if __name__ == "__main__":
    main()
    main()
