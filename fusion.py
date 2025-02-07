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
    parser = ArgumentParser(description="Point Cloud Viewer")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    parser.add_argument('-m', '--mode', type=str, choices=['fusion', 'centroid'], default='fusion',
                        help="Select mode: 'fusion' for all points, 'centroid' for cluster centroids [Default: 'fusion']")
    return parser.parse_args()


def process_point_cloud(msg, is_fusion_mode=True):
    point_cloud = PointCloud2.deserialize(msg.value.payload)

    print(f"Frame ID: {point_cloud.header.frame_id}")
    print(f"Points: {point_cloud.width} x {point_cloud.height}")

    num_points = point_cloud.width * point_cloud.height
    point_size = point_cloud.point_step
    points = []

    data_bytes = bytes(point_cloud.data)
    
    for i in range(num_points):
        offset = i * point_size
        point_data = data_bytes[offset:offset + point_size]
        
        # Unpack common values
        x = struct.unpack('f', point_data[0:4])[0]
        y = struct.unpack('f', point_data[4:8])[0]
        z = struct.unpack('f', point_data[8:12])[0]
        speed = struct.unpack('f', point_data[12:16])[0]
        
        if is_fusion_mode:
            power = struct.unpack('f', point_data[16:20])[0]
            rcs = struct.unpack('f', point_data[20:24])[0]
            cluster_id = struct.unpack('f', point_data[24:28])[0]
            fusion_class = struct.unpack('f', point_data[28:32])[0]
            vision_class = struct.unpack('f', point_data[32:36])[0]
            point_dict = {
                'x': x, 'y': y, 'z': z,
                'speed': speed, 'power': power, 'rcs': rcs,
                'cluster_id': cluster_id,
                'fusion_class': fusion_class,
                'vision_class': vision_class
            }
        else:
            count = struct.unpack('f', point_data[16:20])[0]
            cluster_id = struct.unpack('f', point_data[20:24])[0]
            fusion_class = struct.unpack('f', point_data[24:28])[0]
            vision_class = struct.unpack('f', point_data[28:32])[0]
            point_dict = {
                'x': x, 'y': y, 'z': z,
                'speed': speed, 'count': count,
                'cluster_id': cluster_id,
                'fusion_class': fusion_class,
                'vision_class': vision_class
            }
        
        points.append(point_dict)

    # Print appropriate header based on mode
    if is_fusion_mode:
        header = "    X       Y       Z    Speed   Power    RCS   ClusterId  FusionClass  VisionClass"
        print(header.center(85))
        print("-" * 85)
    else:
        header = "    X       Y       Z    Speed   Count  ClusterId  FusionClass  VisionClass"
        print(header.center(75))
        print("-" * 75)
    
    # Print points with appropriate format
    for point in points:
        if is_fusion_mode:
            line = (
                f"{point['x']:^7.2f} {point['y']:^7.2f} {point['z']:^7.2f} "
                f"{point['speed']:^7.2f} {point['power']:^7.2f} {point['rcs']:^7.2f} "
                f"{point['cluster_id']:^9.0f} {point['fusion_class']:^11.0f} {point['vision_class']:^7.0f}"
            )
            print(line.center(85))
        else:
            line = (
                f"{point['x']:^7.2f} {point['y']:^7.2f} {point['z']:^7.2f} "
                f"{point['speed']:^7.2f} {point['count']:^7.0f} "
                f"{point['cluster_id']:^8.0f} {point['fusion_class']:^11.0f} {point['vision_class']:^7.0f}"
            )
            print(line.center(75))
    
    print(f"\nTotal points: {len(points)}")

def main():
    args = parse_args()
    cfg = zenoh.Config()
    cfg.insert_json5(zenoh.config.CONNECT_KEY, '["%s"]' % args.connect)
    session = zenoh.open(cfg)

    # Subscribe to appropriate topic based on mode
    topic = 'rt/fusion/targets' if args.mode == 'fusion' else 'rt/fusion/occupancy'
    is_fusion_mode = args.mode == 'fusion'
    
    sub = session.declare_subscriber(
        topic,
        lambda msg: process_point_cloud(msg, is_fusion_mode)
    )

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
