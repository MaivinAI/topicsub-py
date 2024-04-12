import zenoh
import time

from sensor_msgs.msg.CameraInfo import CameraInfo
from sensor_msgs.msg.Gps import Gps
from sensor_msgs.msg.Imu import Imu
from sensor_msgs.msg.NavSatStatus import NavSatStatus
from sensor_msgs.msg.PointCloud2 import PointCloud2
from sensor_msgs.msg.RadCube import RadCube

def cam_info_listener(sample):
    out = CameraInfo.deserialize(sample.value.payload)
    print(out)

def gps_listener(sample):
    out = Gps.deserialize(sample.value.payload)
    print(out)

def imu_listener(sample):
    out = Imu.deserialize(sample.value.payload)
    print(out)

def navsatstatus_listener(sample):
    out = NavSatStatus.deserialize(sample.value.payload)
    print(out)

def pc2_listener(sample):
    out = PointCloud2.deserialize(sample.value.payload)
    print(out)

def radcube_listener(sample):
    out = RadCube.deserialize(sample.value.payload)
    print(out)

key1 = 'edgefirst/camerainfo'
key2 = 'edgefirst/gps'
key3 = 'edgefirst/imu'
key4 = 'edgefirst/navsatstatus'
key5 = 'edgefirst/pointcloud2'
key6 = 'edgefirst/radcube'

z1 = zenoh.open()
sub1 = z1.declare_subscriber(key1, cam_info_listener)
z2 = zenoh.open()
sub2 = z2.declare_subscriber(key2, gps_listener)
z3 = zenoh.open()
sub3 = z3.declare_subscriber(key3, imu_listener)
z4 = zenoh.open()
sub4 = z4.declare_subscriber(key4, navsatstatus_listener)
z5 = zenoh.open()
sub5 = z5.declare_subscriber(key5, pc2_listener)
z6 = zenoh.open()
sub6 = z6.declare_subscriber(key6, radcube_listener)

time.sleep(15)

sub1.undeclare()
sub2.undeclare()
sub3.undeclare()
sub4.undeclare()
sub5.undeclare()
sub6.undeclare()
