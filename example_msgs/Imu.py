from dataclasses import dataclass, field
import copy
from pycdr2 import IdlStruct
from pycdr2.types import float64, int32, uint32, array

def default_field(obj):
    return field(default_factory=lambda: copy.copy(obj))

@dataclass
class Quaternion(IdlStruct, typename='Quaternion'):
    x: float64 = 0
    y: float64 = 0
    z: float64 = 0
    w: float64 = 1

@dataclass
class Vector3(IdlStruct, typename='Vector3'):
    x: float64 = 0
    y: float64 = 0
    z: float64 = 0

@dataclass
class Time(IdlStruct, typename='Time'):
    sec: int32 = 0
    nanosec: uint32 = 0

@dataclass
class Header(IdlStruct, typename='Header'):
    stamp: Time = Time()
    frame_id: str = ''

@dataclass
class Imu(IdlStruct, typename='Imu'):
    header: Header = Header()
    orientation: Quaternion = Quaternion()
    orientation_covariance: array[float64, 9] = default_field([0] * 9) # Row major about x, y, z axes
    angular_velocity: Vector3 = Vector3()
    angular_velocity_covariance: array[float64, 9] = default_field([0] * 9) # Row major about x, y, z axes
    linear_acceleration: Vector3 = Vector3()
    linear_acceleration_covariance: array[float64, 9] = default_field([0] * 9) # Row major x, y z

