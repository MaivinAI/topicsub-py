import atexit
import sys
import zenoh
import time
from argparse import ArgumentParser
from edgefirst.schemas.edgefirst_msgs import Mask
from datetime import datetime
import struct
import numpy as np

def parse_args():
    parser = ArgumentParser(description="Imu Example")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    return parser.parse_args()

def fusion_listener(msg):
    fusion = Mask.deserialize(msg.value.payload)
    print(f"\nMask Data:")
    print(f"Dimensions: {fusion.width} x {fusion.height}")
    print(f"Encoding: {fusion.encoding}")
    print(f"Length: {fusion.length}")
    
    try:
        mask_array = np.array(fusion.mask)
        expected_size = fusion.width * fusion.height
        
        if len(mask_array) > expected_size:
            mask_array = mask_array[:expected_size]

        mask_2d = mask_array.reshape(fusion.height, fusion.width)

        binary_mask = (mask_2d > 127).astype(int)

        print("\nOriginal Mask Grid:")
        print("-" * (fusion.width * 4 + 1))
        for row in mask_2d:
            formatted_row = "|" + "|".join(f"{val:^3}" for val in row) + "|"
            print(formatted_row)
            print("-" * (fusion.width * 4 + 1))

        print("\nClassified Mask (0=background (≤127), 1=foreground (>127)):")
        print("-" * (fusion.width * 4 + 1))
        for row in binary_mask:
            formatted_row = "|" + "|".join(f"{val:^3}" for val in row) + "|"
            print(formatted_row)
            print("-" * (fusion.width * 4 + 1))

        print("\nStatistics:")
        print(f"Total pixels: {expected_size}")
        print(f"Foreground pixels (>127): {np.sum(binary_mask)}")
        print(f"Background pixels (≤127): {expected_size - np.sum(binary_mask)}")

        foreground_positions = np.where(binary_mask == 1)
        print("\nForeground pixel positions (row, col):")
        for row, col in zip(foreground_positions[0], foreground_positions[1]):
            print(f"({row}, {col})", end=" ")
        print("\n")
        
    except ValueError as e:
        print(f"\nError processing mask: {e}")

        print("Raw mask data:")
        print(fusion.mask)

def main():
    args = parse_args()
    # Create a Zenoh session using the default configuration plus explicit
    # connection to the local router over TCP at port 7447.  We do this because
    # we currently have scouting disabled to reduce overhead.
    cfg = zenoh.Config()
    cfg.insert_json5(zenoh.config.CONNECT_KEY, '["%s"]' % args.connect)
    session = zenoh.open(cfg)

    # Declare a subscriber on the 'rt/fusion/model_output' topic and print number of boxes
    # and boxes data by decoding the message using the Detect schema.
    sub = session.declare_subscriber('rt/fusion/model_output', fusion_listener)

    # Ensure the session is closed when the script exits
    def _on_exit():
        session.close()
    atexit.register(_on_exit)    

    # The declare_subscriber runs asynchronously, so we need to block the main
    # thread to keep the program running. We use an empty infinite loop to do this
    # but an application could have its main control loop here instead.
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
