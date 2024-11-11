import argparse
import os
import sys

import pandas as pd

sys.path.append("/home/gabriele/Documents/porter")
import porter.sensors.KERNEL_utils as utils


def main():

    file_to_decode = sys.argv[1]

    parser = argparse.ArgumentParser(description="Decode data from the Inclinometer.")

    parser.add_argument("path", type=str, help="Path with the data to be decoded")

    args = parser.parse_args()

    string = args.path.split("/")

    filepath = "/".join(string[:-1])

    if not os.path.exists(filepath + "/decoded"):
        os.mkdir(filepath + "/decoded")

    filename = filepath + "/decoded/" + string[-1][:-4] + ".csv"

    kmsg = utils.KernelMsg()

    dt = kmsg.decode_multi(args.path)

    dataframe = pd.DataFrame(dt)

    dataframe.to_csv(filename, index=False)


if __name__ == "__main__":
    main()
