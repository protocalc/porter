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

    reps = int(len(data) / 20)

    vals = struct.unpack("<" + pattern * reps, data)

    final = np.reshape(np.array(vals), (reps, 3))

    decoded_filename = filepath + "/decoded/" + string[-1][:-4] + ".csv"

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

    np.savetxt(decoded_filename, final)


if __name__ == "__main__":
    main()
