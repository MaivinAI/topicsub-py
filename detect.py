import atexit
import sys
import zenoh
import time
from argparse import ArgumentParser
from edgefirst.schemas.edgefirst_msgs import Detect
from datetime import datetime

def parse_args():
    parser = ArgumentParser(description="Imu Example")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    return parser.parse_args()

def detection_listener(msg):
    detection = Detect.deserialize(bytes(msg.payload))
    print(detection)
    # Generate timestamp from results info
    input_time = detection.input_timestamp.sec + (detection.input_timestamp.nanosec / 1e9)
    date = datetime.fromtimestamp(input_time)
    print("Boxes found at Time: %s - %d" % (str(date), len(detection.boxes)))
    # Loop through all found boxes and display their normalized coordinates
    if len(detection.boxes) > 0:
        for i in range(len(detection.boxes)):
            x = detection.boxes[i].center_x
            y = detection.boxes[i].center_y
            h = detection.boxes[i].height
            w = detection.boxes[i].width
            print("Box %d - X: %.2f Y: %.2f H: %.2f W: %.2f" % (i, x, y, h, w))

def main():
    args = parse_args()
    # Create a Zenoh session using the default configuration plus explicit
    # connection to the local router over TCP at port 7447.  We do this because
    # we currently have scouting disabled to reduce overhead.
    cfg = zenoh.Config()
    cfg.insert_json5("connect", '{ "endpoints": ["%s"] }' % args.connect)
    session = zenoh.open(cfg)

    # Declare a subscriber on the 'rt/model/boxes2d' topic and print number of boxes
    # and boxes data by decoding the message using the Detect schema.
    sub = session.declare_subscriber('rt/model/boxes2d', detection_listener)

    # Ensure the session is closed when the script exits
    def _on_exit():
        session.close()
    atexit.register(_on_exit)    

    # The declare_subscriber runs asynchronously, so we need to block the main
    # thread to keep the program running. We use an empty infinite loop to do this
    # but an application could have its main control loop here instead.
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
        session.close()
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
