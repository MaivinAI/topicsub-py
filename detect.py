import atexit
import signal
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
    parser.add_argument('-t', '--time', type=float, default=5,
                        help="Time to run the subscriber before exiting.")
    return parser.parse_args()

def detection_listener(msg):
    detection = Detect.deserialize(msg.value.payload)
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
    cfg.insert_json5(zenoh.config.CONNECT_KEY, '["%s"]' % args.connect)
    session = zenoh.open(cfg)

    # Ensure the session is closed when the script exits
    def _on_exit():
        session.close()
    atexit.register(_on_exit)

    # Declare a subscriber on the 'rt/gps' topic and print lat/long data by
    # decoding the message using the NavSat schema.
    sub = session.declare_subscriber('rt/detect/boxes2d', detection_listener)

    # The declare_subscriber runs asynchronously, so we need to block the main
    # thread to keep the program running.  We use time.sleep() to do this
    # but an application could have its main control loop here instead.
    time.sleep(args.time)
    sub.undeclare()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
