import os
import sys

import pandas as pd
from pyubx2.ubxreader import UBXReader


def read(stream):
    """
    Reads and parses UBX message data from stream.
    """

    data = {}

    ubr = UBXReader(stream, parsing=True)

    for raw_data, parsed_data in ubr:

        tmp = parsed_data.__dict__

        if parsed_data.identity in data.keys():
            if parsed_data.identity[:3] == "RXM":
                data[parsed_data.identity] += raw_data
            else:
                for i in tmp.keys():
                    if i[0] != "_":
                        if i in data[parsed_data.identity].keys():
                            data[parsed_data.identity][i].append(tmp[i])
                        else:
                            data[parsed_data.identity][i] = []
                            data[parsed_data.identity][i].append(tmp[i])
        else:
            data[parsed_data.identity] = {}

            if parsed_data.identity[:3] == "RXM":
                data[parsed_data.identity] = raw_data
            else:
                for i in tmp.keys():
                    if i[0] != "_":
                        data[parsed_data.identity][i] = []
                        data[parsed_data.identity][i].append(tmp[i])

    return data


def main():

    file_to_decode = sys.argv[1]

    string = file_to_decode.split("/")

    path = "/".join(string[:-1])

    if not os.path.exists(path + "/decoded"):
        os.mkdir(path + "/decoded")

    with open(file_to_decode, "rb") as fstream:
        data = read(fstream)

    for key in data.keys():

        if key[:3] == "RXM":
            filename = path + "/decoded/" + str(key) + "_" + string[-1][:-4] + ".bin"
            with open(filename, "wb") as fd:
                fd.write(data[key])
        else:
            filename = path + "/decoded/" + str(key) + "_" + string[-1][:-4] + ".csv"

            dataframe = pd.DataFrame(data[key])

            dataframe.to_csv(filename, index=False)


if __name__ == "__main__":
    main()
