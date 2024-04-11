# copyright Copyright (c) Seeed Technology Co.,Ltd.
default_scope = 'sscma'

# defaults input type image
input_type = 'image'

# ========================Suggested optional parameters========================
# RUNNING
# Model validation interval in epoch
val_interval = 5
# Model weight saving interval in epochs
save_interval = val_interval

# ================================END=================================
# hooks
default_hooks = dict(
    timer=dict(type='IterTimerHook'),
    logger=dict(type='TextLoggerHook', interval=100),
    param_scheduler=dict(type='ParamSchedulerHook'),
    checkpoint=dict(type='CheckpointHook', interval=save_interval),
    sampler_seed=dict(type='DistSamplerSeedHook'),
    visualization=dict(type='Posevisualization'),
)

# custom hooks
custom_hooks = [
    # Synchronize model buffers such as running_mean and running_var in BN
    # at the end of each epoch
    dict(type='SyncBuffersHook')
]

# multi-processing backend
env_cfg = dict(
    cudnn_benchmark=False,
    mp_cfg=dict(mp_start_method='fork', opencv_num_threads=0),
    dist_cfg=dict(backend='nccl'),
)

# visualizer
vis_backends = [
    dict(type='LocalVisBackend'),
    # dict(type='TensorboardVisBackend'),
    # dict(type='WandbVisBackend'),
]
visualizer = dict(type='mmpose.PoseLocalVisualizer', radius=1, vis_backends=vis_backends, name='visualizer')

# logger
log_processor = dict(type='LogProcessor', window_size=50, by_epoch=True, num_digits=6)
log_level = 'INFO'
load_from = None
resume = False

# file I/O backend
backend_args = dict(backend='local')

# training/validation/testing progress
train_cfg = dict(by_epoch=True, max_epochs=210, val_interval=val_interval)
val_cfg = dict()
test_cfg = dict()
