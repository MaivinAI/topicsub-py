from dataclasses import dataclass, field
import copy
from pycdr2 import IdlStruct
from pycdr2.types import int8, uint16

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

