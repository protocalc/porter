import sys
import os
import pandas as pd

import porter.sensors.KERNEL_utils as utils


def main():

    file_to_decode = sys.argv[1]

    string = file_to_decode.split("/")

    filename = "/".join(string[:-1])

    if not os.path.exists(filename + "/decoded"):
        os.mkdir(filename + "/decoded")

    filename = filename + "/decoded/" + string[-1][:-4] + ".csv"

    kmsg = utils.KernelMsg()

    dt = kmsg.decode_multi(file_to_decode)

    dataframe = pd.DataFrame(dt)

    dataframe.to_csv(filename)


if __name__ == "__main__":
    main()
