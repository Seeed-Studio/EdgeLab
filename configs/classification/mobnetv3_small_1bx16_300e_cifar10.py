_base_ = "../_base_/default_runtime_cls.py"
default_scope = "edgelab"
custom_imports = dict(imports=["edgelab"], allow_failed_imports=False)

# model settings
num_classes = 10

# dataset settings
dataset_type = "mmcls.CIFAR10"
data_root = "datasets"
height = 32
width = 32
batch_size = 16
workers = 1
persistent_workers = True

# optimizer
lr = 0.01
epochs = 300

model = dict(
    type='edgelab.ImageClassifier',
    backbone=dict(type='mmcls.MobileNetV3', arch='small'),
    neck=dict(type='mmcls.GlobalAveragePooling'),
    head=dict(
        type='mmcls.StackedLinearClsHead',
        num_classes=num_classes,
        in_channels=576,
        mid_channels=[1280],
        dropout_rate=0.2,
        act_cfg=dict(type='mmcls.HSwish'),
        loss=dict(type='mmcls.CrossEntropyLoss', loss_weight=1.0),
        init_cfg=dict(type='mmcls.Normal', layer='Linear', mean=0.0, std=0.01, bias=0.0),
        topk=(1, 5),
    ),
)

train_pipeline = [
    dict(type='mmcls.Rotate', angle=30.0, prob=0.6),
    dict(type='mmcls.RandomFlip', prob=0.5, direction='horizontal'),
    dict(type="mmengine.Resize", scale=(height, width)),
    dict(type='mmcls.PackClsInputs'),
]

test_pipeline = [
    dict(type="mmengine.Resize", scale=(height, width)),
    dict(type='mmcls.PackClsInputs'),
]

train_dataloader = dict(
    # Training dataset configurations
    batch_size=batch_size,
    num_workers=workers,
    persistent_workers=persistent_workers,
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        data_prefix='cifar10/',
        test_mode=False,
        pipeline=train_pipeline,
    ),
    sampler=dict(type='DefaultSampler', shuffle=True),
)

val_dataloader = dict(
    batch_size=batch_size,
    num_workers=workers,
    persistent_workers=persistent_workers,
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        data_prefix='cifar10/',
        test_mode=True,
        pipeline=test_pipeline,
    ),
    sampler=dict(type='DefaultSampler', shuffle=False),
)

test_dataloader = val_dataloader

# evaluator
val_evaluator = dict(type='mmcls.Accuracy', topk=(1, 5))
test_evaluator = val_evaluator


val_cfg = dict()
test_cfg = dict()

# optimizer
optim_wrapper = dict(optimizer=dict(type='SGD', lr=lr, momentum=0.9, weight_decay=0.0001))
# learning policy
param_scheduler = dict(type='MultiStepLR', by_epoch=True, milestones=[100, 150], gamma=0.1)

auto_scale_lr = dict(base_batch_size=batch_size)

train_cfg = dict(by_epoch=True, max_epochs=epochs)
