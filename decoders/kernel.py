import argparse
import os
import sys
import yaml

import pandas as pd
import numpy as np

sys.path.append("/home/gabriele/Documents/porter")
import porter.sensors.KERNEL_utils as utils


import matplotlib.pyplot as plt


def main():

    file_to_decode = sys.argv[1]

    parser = argparse.ArgumentParser(description="Decode data from the Inclinometer.")

    parser.add_argument("path", type=str, help="Path with the data to be decoded")
    parser.add_argument(
        "--UDD", default=False, help="Flag to check if UDD message is expected"
    )
    parser.add_argument(
        "--UDD_schema", type=str, help="Path with yaml config file for the flight"
    )

    args = parser.parse_args()

    if args.UDD:
        with open(args.UDD_schema, "r") as cfg:
            config = yaml.safe_load(cfg)
        UDD = True
        UDD_schema = config["sensors"]["Inclinometer_1"]["configuration"]["UDD_data"]
    else:
        UDD = False
        UDD_schema = None

    string = args.path.split("/")

    filepath = "/".join(string[:-1])

    if not os.path.exists(filepath + "/decoded"):
        os.mkdir(filepath + "/decoded")

    filename = filepath + "/decoded/" + string[-1][:-4] + ".csv"

    kmsg = utils.KernelMsg()

    dt = kmsg.decode_multi(args.path, UDD, UDD_schema)

    dataframe = pd.DataFrame(dt)

    print(dataframe)

    dataframe.to_csv(filename, index=False)


if __name__ == "__main__":
    main()
