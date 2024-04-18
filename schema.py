import atexit
import signal
import sys
import zenoh
import time
from argparse import ArgumentParser

ENCODING_PREFIX = str(zenoh.Encoding.APP_OCTET_STREAM())

def parse_args():
    parser = ArgumentParser(description="Topics Example")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    parser.add_argument('-t', '--time', type=float, default=5,
                        help="Time to run the subscriber before exiting.")
    parser.add_argument('topic', type=str, help='The topic to which to subscribe')
    return parser.parse_args()


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

    # Declare a subscriber on the requested topic and print the schema name for
    # this topic.
    sub = session.declare_subscriber(args.topic, lambda msg:
        print(str(msg.encoding).replace(ENCODING_PREFIX, '')))

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
