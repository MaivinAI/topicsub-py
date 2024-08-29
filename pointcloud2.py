import atexit
import sys
import time
import struct
from datetime import datetime
from argparse import ArgumentParser
import zenoh
from edgefirst.schemas.sensor_msgs import PointCloud2, PointFieldDatatype


def parse_args():
    parser = ArgumentParser(description="PointCloud2 Example")
    parser.add_argument(
        '-c',
        '--connect',
        type=str,
        default='tcp/127.0.0.1:7447',
        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    return parser.parse_args()


def pc2_listener(msg):
    pc2 = PointCloud2.deserialize(msg.value.payload)
    endian_format = ">" if pc2.is_bigendian else "<"

    # Format the timestamp from the provided message
    # The date is ignored due to lack of relevance and incorrectness
    message_time = pc2.header.stamp.sec + (pc2.header.stamp.nanosec // 1e9)
    dt = datetime.fromtimestamp(message_time)
    s = dt.strftime('%H:%M:%S')
    s += '.' + str(int(pc2.header.stamp.nanosec % 1000000000)).zfill(9)
    print("PointCloud2 Message received at %s" % s)
    print("Total Points: %d" % (pc2.height * pc2.width))

    # Loop through all points in the PointCloud message
    for i in range(pc2.height):
        for j in range(pc2.width):
            point_start = (i * pc2.width + j) * pc2.point_step
            # Loop through the provided Fields for each Point (x, y, z, speed,
            # power, rcs)
            for f in pc2.fields:
                val = 0
                # Decode the data according to the datatype and endian format stated
                # in the message, location in the array block determined
                # through the offset
                if f.datatype == PointFieldDatatype.FLOAT32.value:
                    arr = bytearray(
                        pc2.data[(point_start + f.offset):(point_start + f.offset + 4)])
                    val = struct.unpack(
                        f'{endian_format}f', arr)[0]
                elif f.datatype == PointFieldDatatype.FLOAT64.value:
                    arr = bytearray(
                        pc2.data[(point_start + f.offset):(point_start + f.offset + 4)])
                    val = struct.unpack(
                        f'{endian_format}f', arr)[0]

                print("%s: %.4f" % (f.name, val), end=' ')
            print()
    print()


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

    # Declare a subscriber on the 'rt/radar/targets' topic and print the pointcloud2 data by
    # decoding the message using the PointCloud2 schema.
    sub = session.declare_subscriber('rt/radar/targets', pc2_listener)

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
