from dataclasses import dataclass, field
import copy
from pycdr2 import IdlStruct
from pycdr2.types import uint8, uint16, float32, int16, int32, uint32, sequence

def default_field(obj):
    return field(default_factory=lambda: copy.copy(obj))

@dataclass
class Time(IdlStruct, typename='Time'):
    sec: int32 = 0
    nanosec: uint32 = 0

@dataclass
class Header(IdlStruct, typename='Header'):
    stamp: Time = Time()
    frame_id: str = ''

@dataclass
class RadCube(IdlStruct, typename='RadCube'):
    RANGE: uint8 = 0
    DOPPLER: uint8 = 0
    AZIMUTH: uint8 = 0
    ELEVATION: uint8 = 0
    RXCHANNEL: uint8 = 0
    SEQUENCE: uint8 = 0
    header: Header = Header()
    layout: sequence[uint8] = default_field([]) # Radar cube layout provides labels for each dimensions
    shape: sequence[uint16] = default_field([]) # Radar cube shape provides the shape of each dimensions
    scales: sequence[float32] = default_field([]) # The scaling factors for the dimensions representing bins.
    cube: sequence[int16] = default_field([]) # The radar cube data as 16bit integers.  If the is_complex
    is_complex: bool = False # True if the radar cube is complex

