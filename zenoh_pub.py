import zenoh
from sensor_msgs.msg.CameraInfo import CameraInfo
from sensor_msgs.msg.Gps import Gps
from sensor_msgs.msg.Imu import Imu
from sensor_msgs.msg.NavSatStatus import NavSatStatus
from sensor_msgs.msg.PointCloud2 import PointCloud2
from sensor_msgs.msg.RadCube import RadCube

s1 = zenoh.open()
key1 = 'edgefirst/camerainfo'
pub1 = s1.declare_publisher(key1)
s2 = zenoh.open()
key2 = 'edgefirst/gps'
pub2 = s2.declare_publisher(key2)
s3 = zenoh.open()
key3 = 'edgefirst/imu'
pub3 = s3.declare_publisher(key3)
s4 = zenoh.open()
key4 = 'edgefirst/navsatstatus'
pub4 = s4.declare_publisher(key4)
s5 = zenoh.open()
key5 = 'edgefirst/pointcloud2'
pub5 = s5.declare_publisher(key5)
s6 = zenoh.open()
key6 = 'edgefirst/radcube'
pub6 = s6.declare_publisher(key6)

cmd1 = CameraInfo()
cmd2 = Gps()
cmd3 = Imu()
cmd4 = NavSatStatus()
cmd5 = PointCloud2()
cmd6 = RadCube()
pub1.put(cmd1.serialize())
pub2.put(cmd2.serialize())
pub3.put(cmd3.serialize())
pub4.put(cmd4.serialize())
pub5.put(cmd5.serialize())
pub6.put(cmd6.serialize())
