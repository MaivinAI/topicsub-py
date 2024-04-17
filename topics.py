import atexit
import signal
import sys
import zenoh
import time
from argparse import ArgumentParser

ENCODING_PREFIX = str(zenoh.Encoding.APP_OCTET_STREAM())
detected_msgs = {}  


def parse_args():
    parser = ArgumentParser(description="Topics Example")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    parser.add_argument('-t', '--time', type=float, default=5,
                        help="Time to run the subscriber before exiting.")
    return parser.parse_args()


def all_listener(msg):
    msg_key = str(msg.key_expr)
    if msg_key in detected_msgs.keys():
        return
    encoding = str(msg.encoding)
    if encoding.startswith(ENCODING_PREFIX):
        msg_type = encoding.replace(ENCODING_PREFIX, '')
    detected_msgs[msg_key] = msg_type
    print("New Topic Found: %s --> %s" % (msg_key, msg_type)) 


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
    # sub0 = session.declare_subscriber('rt/gps', lambda msg:
    #     print(str(msg.encoding).removeprefix(ENCODING_PREFIX)))
    sub = session.declare_subscriber('rt/**', all_listener)

    # The declare_subscriber runs asynchronously, so we need to block the main
    # thread to keep the program running.  We use signal.pause() to do this
    # but an application could have its main control loop here instead.
    # signal.pause()
    time.sleep(args.time)
    sub.undeclare()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)