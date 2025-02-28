import atexit
import sys
import zenoh
import time
from argparse import ArgumentParser
from edgefirst.schemas.sensor_msgs import NavSatFix

def parse_args():
    parser = ArgumentParser(description="NavSat Example")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    return parser.parse_args()

def gps_listener(msg):
    gps = NavSatFix.deserialize(bytes(msg.payload))
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
    cfg.insert_json5("connect", '{ "endpoints": ["%s"] }' % args.connect)
    session = zenoh.open(cfg)

    # Ensure the session is closed when the script exits
    def _on_exit():
        session.close()
    atexit.register(_on_exit)

    # Declare a subscriber on the 'rt/gps' topic and print lat/long data by
    # decoding the message using the NavSat schema.
    sub = session.declare_subscriber('rt/gps', gps_listener)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
        session.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
