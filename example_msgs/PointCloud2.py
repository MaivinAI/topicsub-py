from dataclasses import dataclass, field
import copy
from pycdr2 import IdlStruct
from pycdr2.types import uint32, uint8, int32, sequence

def default_field(obj):
    return field(default_factory=lambda: copy.copy(obj))

@dataclass
class PointField(IdlStruct, typename='PointField'):
    INT8: uint8 = 0
    UINT8: uint8 = 0
    INT16: uint8 = 0
    UINT16: uint8 = 0
    INT32: uint8 = 0
    UINT32: uint8 = 0
    FLOAT32: uint8 = 0
    FLOAT64: uint8 = 0
    name: str = '' # Name of field
    offset: uint32 = 0 # Offset from start of point struct
    datatype: uint8 = 0 # Datatype enumeration, see above
    count: uint32 = 0 # How many elements in the field

@dataclass
class Time(IdlStruct, typename='Time'):
    sec: int32 = 0
    nanosec: uint32 = 0

@dataclass
class Header(IdlStruct, typename='Header'):
    stamp: Time = Time()
    frame_id: str = ''

@dataclass
class PointCloud2(IdlStruct, typename='PointCloud2'):
    header: Header = Header()
    height: uint32 = 0
    width: uint32 = 0
    fields: sequence[PointField] = default_field([])
    is_bigendian: bool = False # Is this data bigendian?
    point_step: uint32 = 0 # Length of a point in bytes
    row_step: uint32 = 0 # Length of a row in bytes
    data: sequence[uint8] = default_field([]) # Actual point data, size is (row_step*height)
    is_dense: bool = False # True if there are no invalid points

