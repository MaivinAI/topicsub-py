import atexit
import signal
import sys
import zenoh
from edgefirst.schemas.sensor_msgs import CameraInfo


def main():
    # Create a Zenoh session using the default configuration plus explicit
    # connection to the local router over TCP at port 7447.  We do this because
    # we currently have scouting disabled to reduce overhead.
    cfg = zenoh.Config()
    cfg.insert_json5(zenoh.config.CONNECT_KEY, '["tcp/127.0.0.1:7447"]')
    session = zenoh.open(cfg)

    # Ensure the session is closed when the script exits
    def _on_exit():
        session.close()
    atexit.register(_on_exit)

    # Declare a subscriber on the 'rt/camera/info' topic and print each message
    # with the CameraInfo schema.
    sub = session.declare_subscriber(
        'rt/camera/info',
        lambda msg: print(CameraInfo.deserialize(msg.value.payload)))

    # The declare_subscriber runs asynchronously, so we need to block the main
    # thread to keep the program running.  We use signal.pause() to do this
    # but an application could have its main control loop here instead.
    signal.pause()
    sub.undeclare()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
