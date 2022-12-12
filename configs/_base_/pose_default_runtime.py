checkpoint_config = dict(interval=10)

log_config = dict(
    interval=5,
    hooks=[
        dict(type='TextLoggerHook', ndigits=6),
        # dict(type='TensorboardLoggerHook')
        # dict(type='PaviLoggerHook') # for internal services
    ])

log_level = 'INFO'
load_from = None
resume_from = None
dist_params = dict(backend='nccl')
workflow = [('train', 1)]

# disable opencv multithreading to avoid system being overloaded
opencv_num_threads = 1
# set multi-process start method as `fork` to speed up the training
mp_start_method = 'fork'
