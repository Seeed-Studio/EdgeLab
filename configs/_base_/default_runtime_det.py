# copyright Copyright (c) Seeed Technology Co.,Ltd.
default_scope = 'mmdet'

# defaults input type image
input_type = 'image'

# ========================Suggested optional parameters========================
# RUNNING
# Model validation interval in epoch
val_interval = 5
# Model weight saving interval in epochs
save_interval = val_interval

# ================================END=================================
default_hooks = dict(
    timer=dict(type='IterTimerHook'),
    logger=dict(type='sscma.TextLoggerHook', interval=100),
    param_scheduler=dict(type='ParamSchedulerHook'),
    checkpoint=dict(type='CheckpointHook', interval=save_interval),
    sampler_seed=dict(type='DistSamplerSeedHook'),
    visualization=dict(type='mmdet.DetVisualizationHook'),
)

env_cfg = dict(
    cudnn_benchmark=False,
    mp_cfg=dict(mp_start_method='fork', opencv_num_threads=0),
    dist_cfg=dict(backend='nccl'),
)


vis_backends = [
    dict(type='LocalVisBackend'),
    # dict(type='WandbVisBackend'),
    dict(type='TensorboardVisBackend'),
]
visualizer = dict(type='sscma.FomoLocalVisualizer', vis_backends=vis_backends, name='visualizer')


log_processor = dict(type='LogProcessor', window_size=50, by_epoch=True)

log_level = 'INFO'
load_from = None
resume = False

train_cfg = dict(by_epoch=True, max_epochs=300, val_interval=val_interval)
val_cfg = dict()
test_cfg = dict()
