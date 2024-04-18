import atexit
import signal
import sys
import zenoh
import time
from argparse import ArgumentParser
from edgefirst.schemas.sensor_msgs import NavSatFix

def parse_args():
    parser = ArgumentParser(description="NavSat Example")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    parser.add_argument('-t', '--time', type=float, default=5,
                        help="Time to run the subscriber before exiting.")
    return parser.parse_args()

def gps_listener(msg):
    gps = NavSatFix.deserialize(msg.value.payload)
    lat = gps.latitude
    long = gps.longitude
    print("Latitude: %.6f Longitude: %.6f" % (lat, long))
    ns_dir = 'N'
    ew_dir = 'E'
    if lat < 0:
        ns_dir = 'S'
        lat *= -1
    if long < 0:
        ew_dir = 'W'
        long *= -1
    gps_url = 'https://www.google.com/maps?q=%f%s+%f%s' % (lat, ns_dir, long, ew_dir)
    
    print("Location URL: %s" % gps_url)


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
    sub = session.declare_subscriber('rt/gps', gps_listener)

    # The declare_subscriber runs asynchronously, so we need to block the main
    # thread to keep the program running.  We use signal.pause() to do this
    # but an application could have its main control loop here instead.
    time.sleep(args.time)
    sub.undeclare()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
