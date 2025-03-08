import atexit
import sys
import zenoh
import time
from argparse import ArgumentParser

ENCODING_PREFIX = str(zenoh.Encoding.APPLICATION_OCTET_STREAM)

def parse_args():
    parser = ArgumentParser(description="Topics Example")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    parser.add_argument('topic', type=str, help='The topic to which to subscribe')
    return parser.parse_args()


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
    except zenoh.ZError as e:
        print(f"Failed to open Zenoh session: {e}")
        sys.exit(1)

    # Ensure the session is closed when the script exits
    def _on_exit():
        session.close()
    atexit.register(_on_exit)

    # Declare a subscriber on the requested topic and print the schema name for
    # this topic.
    def msg_callback(msg):
        encoding = str(msg.encoding)
        msg_type = encoding  # Default value
        if ";" in encoding:  # Check if encoding contains a semicolon
            msg_type = encoding.split(";")[1]  # Take the part after the semicolon
        elif encoding.startswith(ENCODING_PREFIX):
            msg_type = encoding.replace(ENCODING_PREFIX, '')
        print(msg_type)

    sub = session.declare_subscriber(args.topic, msg_callback)

    # The declare_subscriber runs asynchronously, so we need to block the main
    # thread to keep the program running.  We use time.sleep() to do this
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
