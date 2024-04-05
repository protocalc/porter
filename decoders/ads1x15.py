import argparse
import struct

import numpy as np


def main():

    parser = argparse.ArgumentParser(description="Decode data from the ADC.")

    parser.add_argument("path", type=str, help="Path with the data to be decoded")

    parser.add_argument(
        "--voltage",
        type=bool,
        action="store_false",
        help="Flag to indicate that the ADC data are saved as voltage",
    )

    args = parser.parse_args()

    string = args.path.split("/")

    filepath = "/".join(string[:-1])

    if not os.path.exists(filepath + "/decoded"):
        os.mkdir(filepath + "/decoded")

    if voltage:
        pattern = "df"
    else:
        pattern = "di"

    with open(args.path, "rb") as fstream:
        data = read(fstream)

    reps = len(data) / 12

    vals = struct.unpack("<" + pattern * reps, data)

    final = np.reshape(np.array(vals), (reps, 2))

    decoded_filename = filepath + "/decoded/" + string[-1][:-4] + ".csv"

    np.savetxt(decoded_filename, final)


if __name__ == "__main__":
    main()
