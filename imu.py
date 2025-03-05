import atexit
import sys
import zenoh
import time
from argparse import ArgumentParser
from edgefirst.schemas.sensor_msgs import Imu

def parse_args():
    parser = ArgumentParser(description="Imu Example")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    return parser.parse_args()

def imu_listener(msg):
    imu = Imu.deserialize(bytes(msg.payload))
    print("x=%f y=%f z=%f" % (
        imu.linear_acceleration.x,
        imu.linear_acceleration.y,
        imu.linear_acceleration.z))


def main():
    args = parse_args()
    # Create a Zenoh session using the default configuration plus explicit
    # connection to the local router over TCP at port 7447.  We do this because
    # we currently have scouting disabled to reduce overhead.
    try:
        cfg = zenoh.Config()
        cfg.insert_json5("mode", "'client'")
        cfg.insert_json5("connect", '{ "endpoints": ["%s"] }' % args.connect)
        session = zenoh.open(cfg)
    except zenoh.ZenohError as e:
        print(f"Failed to open Zenoh session: {e}")
        sys.exit(1)

    # Ensure the session is closed when the script exits
    def _on_exit():
        session.close()
    atexit.register(_on_exit)

    # Declare a subscriber on the 'rt/gps' topic and print lat/long data by
    # decoding the message using the NavSat schema.
    sub = session.declare_subscriber('rt/imu', imu_listener)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
        session.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
