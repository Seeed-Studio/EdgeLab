# Copyright (c) Seeed Technology Co.,Ltd. All rights reserved.
# defaults to use registries in mmpretrain
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
# configure default hooks
default_hooks = dict(
    # record the time of every iteration.
    timer=dict(type='IterTimerHook'),
    # print log every 100 iterations.
    logger=dict(type='TextLoggerHook', interval=100),
    # enable the parameter scheduler.
    param_scheduler=dict(type='ParamSchedulerHook'),
    # save checkpoint per epoch.
    checkpoint=dict(type='CheckpointHook', save_best='auto', interval=save_interval),
    # set sampler seed in distributed evrionment.
    sampler_seed=dict(type='DistSamplerSeedHook'),
    # validation results visualization, set True to enable it.
    visualization=dict(type='sscma.ClsVisualizationHook', enable=False),
)

# configure environment
env_cfg = dict(
    # whether to enable cudnn benchmark
    cudnn_benchmark=False,
    # set multi process parameters
    mp_cfg=dict(mp_start_method='fork', opencv_num_threads=0),
    # set distributed parameters
    dist_cfg=dict(backend='nccl'),
)

# set visualizer
vis_backends = [dict(type='LocalVisBackend')]
visualizer = dict(type='sscma.ClsVisualizer', vis_backends=vis_backends)

# set log level
log_level = 'INFO'

# load from which checkpoint
load_from = None

# whether to resume training from the loaded checkpoint
resume = False

# Defaults to use random seed and disable `deterministic`
randomness = dict(seed=None, deterministic=False)

train_cfg = dict(by_epoch=True, val_interval=val_interval)
