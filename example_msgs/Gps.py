from dataclasses import dataclass, field
import copy
from pycdr2 import IdlStruct
from pycdr2.types import float64, uint8, int8, uint16, int32, uint32, array

def default_field(obj):
    return field(default_factory=lambda: copy.copy(obj))

@dataclass
class NavSatStatus(IdlStruct, typename='NavSatStatus'):
    STATUS_NO_FIX: int8 = 0 # unable to fix position
    STATUS_FIX: int8 = 0 # unaugmented fix
    STATUS_SBAS_FIX: int8 = 0 # with satellite-based augmentation
    STATUS_GBAS_FIX: int8 = 0 # with ground-based augmentation
    status: int8 = 0
    SERVICE_GPS: uint16 = 0
    SERVICE_GLONASS: uint16 = 0
    SERVICE_COMPASS: uint16 = 0 # includes BeiDou.
    SERVICE_GALILEO: uint16 = 0
    service: uint16 = 0

@dataclass
class Time(IdlStruct, typename='Time'):
    sec: int32 = 0
    nanosec: uint32 = 0

@dataclass
class Header(IdlStruct, typename='Header'):
    stamp: Time = Time()
    frame_id: str = ''

@dataclass
class Gps(IdlStruct, typename='Gps'):
    header: Header = Header()
    status: NavSatStatus = NavSatStatus()
    latitude: float64 = 0
    longitude: float64 = 0
    altitude: float64 = 0
    position_covariance: array[float64, 9] = default_field([0] * 9)
    COVARIANCE_TYPE_UNKNOWN: uint8 = 0
    COVARIANCE_TYPE_APPROXIMATED: uint8 = 0
    COVARIANCE_TYPE_DIAGONAL_KNOWN: uint8 = 0
    COVARIANCE_TYPE_KNOWN: uint8 = 0
    position_covariance_type: uint8 = 0

