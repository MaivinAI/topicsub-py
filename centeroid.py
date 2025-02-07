import atexit
import sys
import zenoh
import time
from argparse import ArgumentParser
from edgefirst.schemas.sensor_msgs import PointCloud2
from datetime import datetime
import struct
import numpy as np

def parse_args():
    parser = ArgumentParser(description="Imu Example")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    return parser.parse_args()

def centeroid_listener(msg):
    centeroid = PointCloud2.deserialize(msg.value.payload)

    input_time = centeroid.header.stamp.sec + (centeroid.header.stamp.nanosec / 1e9)
    date = datetime.fromtimestamp(input_time)
    print(f"\nPoint Cloud received at: {date}")
    print(f"Frame ID: {centeroid.header.frame_id}")
    print(f"Points: {centeroid.width} x {centeroid.height}")

    num_points = centeroid.width * centeroid.height
    point_size = centeroid.point_step
    points = []

    data_bytes = bytes(centeroid.data)
    
    for i in range(num_points):
        offset = i * point_size
        point_data = data_bytes[offset:offset + point_size]
        
        # Unpack all float32 values (type 7)
        x = struct.unpack('f', point_data[0:4])[0]
        y = struct.unpack('f', point_data[4:8])[0]
        z = struct.unpack('f', point_data[8:12])[0]
        speed = struct.unpack('f', point_data[12:16])[0]
        count = struct.unpack('f', point_data[16:20])[0]
        cluster_id = struct.unpack('f', point_data[20:24])[0]
        fusion_class = struct.unpack('f', point_data[24:28])[0]
        vision_class = struct.unpack('f', point_data[28:32])[0]
        
        points.append({
            'x': x, 'y': y, 'z': z,
            'speed': speed, 'count': count,
            'cluster_id': cluster_id,
            'fusion_class': fusion_class,
            'vision_class': vision_class
        })

    print("\nPoint Cloud Data:")
    header = "    X       Y       Z    Speed   Count  ClusterId  FusionClass  VisionClass"
    print(header.center(75))
    print("-" * 75)
    
    for point in points:
        line = (
            f"{point['x']:^7.2f} {point['y']:^7.2f} {point['z']:^7.2f} "
            f"{point['speed']:^7.2f} {point['count']:^7.0f} "
            f"{point['cluster_id']:^8.0f} {point['fusion_class']:^11.0f} {point['vision_class']:^7.0f}"
        )
        print(line.center(75))
    
    print(f"\nTotal points: {len(points)}")

def main():
    args = parse_args()
    # Create a Zenoh session using the default configuration plus explicit
    # connection to the local router over TCP at port 7447.  We do this because
    # we currently have scouting disabled to reduce overhead.
    cfg = zenoh.Config()
    cfg.insert_json5(zenoh.config.CONNECT_KEY, '["%s"]' % args.connect)
    session = zenoh.open(cfg)

    # Declare a subscriber on the 'rt/fusion/targets' topic and print number of boxes
    # and boxes data by decoding the message using the Detect schema.
    sub = session.declare_subscriber('rt/fusion/occupancy', centeroid_listener)

    # Ensure the session is closed when the script exits
    def _on_exit():
        session.close()
    atexit.register(_on_exit)    

    # The declare_subscriber runs asynchronously, so we need to block the main
    # thread to keep the program running. We use an empty infinite loop to do this
    # but an application could have its main control loop here instead.
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
