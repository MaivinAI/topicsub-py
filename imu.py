import atexit
import signal
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
    imu = Imu.deserialize(msg.value.payload)
    print("Yaw: %.4f Pitch: %.4f Roll: %.4f" % (imu.orientation.x, imu.orientation.y,
                                                imu.orientation.z))


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
    sub = session.declare_subscriber('rt/imu', imu_listener)

    # The declare_subscriber runs asynchronously, so we need to block the main
    # thread to keep the program running.  We use time.sleep() to do this
    # but an application could have its main control loop here instead.
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
