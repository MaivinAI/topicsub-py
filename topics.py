import zenoh
import time
from argparse import ArgumentParser

ENCODING_PREFIX = str(zenoh.Encoding.APPLICATION_OCTET_STREAM)
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
    msg_type = encoding  # Default value
    if ";" in encoding:  # Check if encoding contains a semicolon
        msg_type = encoding.split(";")[1]  # Take the part after the semicolon
    elif encoding.startswith(ENCODING_PREFIX):
        msg_type = encoding.replace(ENCODING_PREFIX, '')
    
    detected_msgs[msg_key] = msg_type
    print("New Topic Found: %s --> %s" % (msg_key, msg_type))

def main():
    args = parse_args()
    # Create a Zenoh session using the default configuration plus explicit
    # connection to the local router over TCP at port 7447.  We do this because
    # we currently have scouting disabled to reduce overhead.
    cfg = zenoh.Config()
    cfg.insert_json5("mode", "'client'")
    cfg.insert_json5("connect", '{ "endpoints": ["%s"] }' % args.connect)
    session = zenoh.open(cfg)
    try:
        # Declare subscriber that will listen for all the rt/ messages
        sub = session.declare_subscriber('rt/**', all_listener)

        # The declare_subscriber runs asynchronously, so we need to block the main
        # thread to keep the program running.  We use time.sleep() to do this
        # but an application could have its main control loop here instead.
        # signal.pause()
        time.sleep(args.time)

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        if 'sub' in locals():
            sub.undeclare()
        session.close()

if __name__ == "__main__":
    main()