# Copyright (c) Seeed Technology Co.,Ltd. All rights reserved.
from mmengine.config import read_base

with read_base():
    from .pfld_mbv2_1000e import *

from sscma.datasets import MeterData
from sscma.models import (
    PFLD,
    PFLDhead,
    PFLDLoss,
    MobileNetV3,
)
from torch.nn import ReLU
from albumentations import (
    Resize,
    ColorJitter,
    MedianBlur,
    HorizontalFlip,
    VerticalFlip,
    Rotate,
    Affine,
)
from mmengine.dataset import default_collate
from sscma.deploy.models.pfld_infer import PFLDInfer

# ========================Suggested optional parameters========================
# MODEL
num_classes = 1
deepen_factor = 0.33
widen_factor = 0.15

# DATA
dataset_type = MeterData

data_root = ""

train_ann = "train/annotations.txt"
train_data = "train/images"
val_ann = "val/annotations.txt"
val_data = "val/images"

height = 112
width = 112
imgsz = (width, height)

# TRAIN
batch = 32
workers = 4
val_batch = 1
val_workers = 1
lr = 0.0001
epochs = 1000
weight_decay = 1e-6
momentum = (0.9, 0.99)

persistent_workers = True
# ================================END=================================

model = dict(
    type=PFLD,
    backbone=dict(
        type=MobileNetV3,
        inchannel=3,
        arch="large",
        out_indices=(6,),
        widen_factor=1
    ),
    head=dict(
        type=PFLDhead,
        num_point=num_classes,
        input_channel=80,
        act_cfg=ReLU,
        loss_cfg=dict(type=PFLDLoss),
    ),
)

deploy = dict(
    type=PFLDInfer,
)

quantizer_config = dict(
    type=PFLDQuantModel,
    loss_cfg=dict(type=PFLDLoss),
)


train_pipeline = [
    dict(type=Resize, height=imgsz[1], width=imgsz[0], interpolation=0),
    # dict(type="PixelDropout"),
    dict(type=ColorJitter, brightness=0.3, contrast=0.3, saturation=0.3, p=0.5),
    # dict(type='GaussNoise'),
    # dict(type="CoarseDropout",max_height=12,max_width=12),
    dict(type=MedianBlur, blur_limit=3, p=0.5),
    dict(type=HorizontalFlip),
    dict(type=VerticalFlip),
    dict(type=Rotate, limit=45, p=0.7),
    dict(type=Affine, translate_percent=[0.05, 0.3], p=0.6),
]

val_pipeline = [dict(type=Resize, height=imgsz[1], width=imgsz[0])]

train_dataloader = dict(
    batch_size=batch,
    num_workers=workers,
    persistent_workers=True,
    drop_last=False,
    collate_fn=dict(type=default_collate),
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir=train_data,
        index_file=train_ann,
        pipeline=train_pipeline,
    ),
)

val_dataloader = dict(
    batch_size=val_batch,
    num_workers=val_workers,
    persistent_workers=True,
    drop_last=False,
    collate_fn=dict(type=default_collate),
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir=val_data,
        index_file=val_ann,
        pipeline=val_pipeline,
    ),
)
test_dataloader = val_dataloader
