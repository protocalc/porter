import os
import sys
import pandas as pd

from pyubx2.ubxreader import UBXReader


def combine_dict(d1, d2):
    return {
        k: tuple(d[k] for d in (d1, d2) if k in d)
        for k in set(d1.keys()) | set(d2.keys())
    }


def read(stream):
    """
    Reads and parses UBX message data from stream.
    """

    data = {}

    ubr = UBXReader(stream, parsing=True)

    for _, parsed_data in ubr:

        if parsed_data.identity in data.keys():
            data[parsed_data.identity] = combine_dict(
                data[parsed_data.identity], parsed_data._get_dict()
            )
        else:
            data[parsed_data.identity] = parsed_data._get_dict()

    return data


def main():

    file_to_decode = sys.argv[1]

    string = file_to_decode.split("/")

    filename = "/".join(string[:-1])

    if not os.path.exists(filename + "/decoded"):
        os.mkdir(filename + "/decoded")

    with open(file_to_decode, "rb") as fstream:
        data = read(fstream)

    for key in data.keys():

        filename = filename + "/decoded/" + str(key) + "_" + string[-1][:-4] + ".csv"

        dataframe = pd.DataFrame(data[key])

        dataframe.to_csv(filename)


if __name__ == "__main__":
    main()
