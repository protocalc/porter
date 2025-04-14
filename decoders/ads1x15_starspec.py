import numpy as np
import pandas as pd 

import matplotlib.pyplot as plt

def decode_bin_file(file_path):
    decoded_data = []
    try:
        with open(file_path, "rb") as f:
            lines = f.readlines()

        for line in lines:
            # Decode the line from bytes to ASCII and split
            text_line = line.decode("ascii").strip()
            if text_line:
                timestamp, value = text_line.split()
                decoded_data.append((int(timestamp), int(value)))
    except Exception as e:
        print(f"Error decoding file: {e}")

    return decoded_data

# Example usage:
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Decode data from the ADC.")

    parser.add_argument("path", type=str, 
                        help="Path with the data to be decoded")
    parser.add_argument("-p", "--plot", action="store_true",
                        help="Flag to plot the data")

    args = parser.parse_args()
    decoded = decode_bin_file(args.path)
    df = pd.DataFrame(decoded, columns=["timestamp", "amplitude"])
    # Normalize timestamps (optional but helpful for plotting)
    df["timestamp"] = (df["timestamp"] - df["timestamp"].iloc[0]) / 1e9  # convert from ns to seconds
    df["amplitude"] = df["amplitude"].astype(int)
    
    if args.plot:
        fig=plt.figure()
        plt.plot(df["timestamp"], df["amplitude"])
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.show()
