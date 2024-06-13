# Copyright (c) Seeed Technology Co.,Ltd. All rights reserved.
_base_ = './base.py'
# ========================Suggested optional parameters========================
# MODEL
num_classes = 10
widen_factor = 1.0

# DATA
dataset_type = 'sscma.CIFAR10'
data_root = 'datasets/'
train_ann = ''
train_data = 'cifar10/'
val_ann = ''
val_data = 'cifar10/'
# ================================END=================================

model = dict(
    type='sscma.ImageClassifier',
    backbone=dict(type='sscma.MobileNetV2', widen_factor=widen_factor, out_indices=(7,)),
    neck=dict(type='sscma.GlobalAveragePooling'),
    head=dict(
        type='sscma.LinearClsHead',
        in_channels=1280,
        num_classes=num_classes,
    ),
)
train_dataloader = dict(
    # Training dataset configurations
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        data_prefix=train_data,
        test_mode=False,
    ),
)

val_dataloader = dict(
    # Valid dataset configurations
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        data_prefix=val_data,
        test_mode=True,
    ),
)

test_dataloader = val_dataloader
