from .axes_head import AxesClsHead
from .cls_head import Audio_head
from .fastestdet_head import Fastest_Head
from .fomo_head import FomoHead
from .pfld_head import PFLDhead
from .taggregate_head import TAggregate
from .yolo_head import YOLOV5Head

__all__ = [
    'Audio_head',
    'TAggregate',
    'PFLDhead',
    'Fastest_Head',
    'FomoHead',
    'AxesClsHead',
    'YOLOV5Head',
]
