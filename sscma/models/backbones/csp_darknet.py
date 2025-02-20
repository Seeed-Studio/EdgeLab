# Copyright (c) Seeed Technology Co.,Ltd.
# Copyright (c) OpenMMLab.
import math
from typing import List, Tuple, Union

import torch
import torch.nn as nn
from torch.nn.modules.batchnorm import _BatchNorm

from mmengine.model import BaseModule
from sscma.utils import ConfigType, OptMultiConfig
from ..cnn import (
    ConvModule,
    DepthwiseSeparableConvModule,
)
from ..layers import CSPLayer
from ..necks.sppf import SPPFBottleneck
from ..utils import make_divisible, make_round
from .base_backbone import YOLOBaseBackbone


class YOLOv5CSPDarknet(YOLOBaseBackbone):
    arch_settings = {
        "P5": [
            [64, 128, 3, True, False],
            [128, 256, 6, True, False],
            [256, 512, 9, True, False],
            [512, 1024, 3, True, True],
        ],
        "P6": [
            [64, 128, 3, True, False],
            [128, 256, 6, True, False],
            [256, 512, 9, True, False],
            [512, 768, 3, True, False],
            [768, 1024, 3, True, True],
        ],
    }

    def __init__(
        self,
        arch: str = "P5",
        plugins: Union[dict, List[dict]] = None,
        deepen_factor: float = 1.0,
        widen_factor: float = 1.0,
        input_channels: int = 3,
        out_indices: Tuple[int] = (2, 3, 4),
        frozen_stages: int = -1,
        norm_cfg: ConfigType = dict(type="BN", momentum=0.03, eps=0.001),
        act_cfg: ConfigType = dict(type="SiLU", inplace=True),
        norm_eval: bool = False,
        init_cfg: OptMultiConfig = None,
    ):
        self.arch = arch
        super().__init__(
            self.arch_settings[arch],
            deepen_factor,
            widen_factor,
            input_channels=input_channels,
            out_indices=out_indices,
            plugins=plugins,
            frozen_stages=frozen_stages,
            norm_cfg=norm_cfg,
            act_cfg=act_cfg,
            norm_eval=norm_eval,
            init_cfg=init_cfg,
        )

    def build_stem_layer(self):
        return ConvModule(
            self.input_channels,
            make_divisible(self.arch_settings[self.arch][0][0], self.widen_factor),
            kernel_size=6,
            stride=2,
            padding=2,
            norm_cfg=self.norm_cfg,
            act_cfg=self.act_cfg,
        )

    def build_stage_layer(self, stage_idx: int, setting: list) -> list:
        in_channels, out_channels, num_blocks, add_identity, use_spp = setting

        in_channels = make_divisible(in_channels, self.widen_factor)
        out_channels = make_divisible(out_channels, self.widen_factor)
        num_blocks = make_round(num_blocks)
        stage = []
        conv_layer = ConvModule(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=2,
            padding=1,
            norm_cfg=self.norm_cfg,
            act_cfg=self.act_cfg,
        )
        stage.append(conv_layer)

        csp_layer = CSPLayer(
            out_channels,
            out_channels,
            num_blocks=num_blocks,
            add_identity=add_identity,
            norm_cfg=self.norm_cfg,
            act_cfg=self.act_cfg,
        )
        stage.append(csp_layer)

        if use_spp:
            spp = SPPFBottleneck(
                out_channels,
                out_channels,
                kernel_sizes=5,
                norm_cfg=self.norm_cfg,
                act_cfg=self.act_cfg,
            )
            stage.append(spp)
        return stage

    def init_weights(self):
        if self.init_cfg is None:
            for m in self.modules():
                if isinstance(m, torch.nn.Conv2d):
                    m.reset_parameters()
        else:
            super().init_weights()


class Focus(nn.Module):
    """Focus width and height information into channel space.

    Args:
        in_channels (int): The input channels of this Module.
        out_channels (int): The output channels of this Module.
        kernel_size (int): The kernel size of the convolution. Default: 1
        stride (int): The stride of the convolution. Default: 1
        conv_cfg (dict): Config dict for convolution layer. Default: None,
            which means using conv2d.
        norm_cfg (dict): Config dict for normalization layer.
            Default: dict(type='BN', momentum=0.03, eps=0.001).
        act_cfg (dict): Config dict for activation layer.
            Default: dict(type='Swish').
    """

    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size=1,
        stride=1,
        conv_cfg=None,
        norm_cfg=dict(type="BN", momentum=0.03, eps=0.001),
        act_cfg=dict(type="Swish"),
    ):
        super().__init__()
        self.conv = ConvModule(
            in_channels * 4,
            out_channels,
            kernel_size,
            stride,
            padding=(kernel_size - 1) // 2,
            conv_cfg=conv_cfg,
            norm_cfg=norm_cfg,
            act_cfg=act_cfg,
        )

    def forward(self, x):
        # shape of x (b,c,w,h) -> y(b,4c,w/2,h/2)
        patch_top_left = x[..., ::2, ::2]
        patch_top_right = x[..., ::2, 1::2]
        patch_bot_left = x[..., 1::2, ::2]
        patch_bot_right = x[..., 1::2, 1::2]
        x = torch.cat(
            (
                patch_top_left,
                patch_bot_left,
                patch_top_right,
                patch_bot_right,
            ),
            dim=1,
        )
        return self.conv(x)


class SPPBottleneck(BaseModule):
    """Spatial pyramid pooling layer used in YOLOv3-SPP.

    Args:
        in_channels (int): The input channels of this Module.
        out_channels (int): The output channels of this Module.
        kernel_sizes (tuple[int]): Sequential of kernel sizes of pooling
            layers. Default: (5, 9, 13).
        conv_cfg (dict): Config dict for convolution layer. Default: None,
            which means using conv2d.
        norm_cfg (dict): Config dict for normalization layer.
            Default: dict(type='BN').
        act_cfg (dict): Config dict for activation layer.
            Default: dict(type='Swish').
        init_cfg (dict or list[dict], optional): Initialization config dict.
            Default: None.
    """

    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_sizes=(5, 9, 13),
        conv_cfg=None,
        norm_cfg=dict(type="BN", momentum=0.03, eps=0.001),
        act_cfg=dict(type="Swish"),
        split_max_pool_kernel=False,
        init_cfg=None,
    ):
        super().__init__(init_cfg)
        mid_channels = in_channels // 2
        self.conv1 = ConvModule(
            in_channels,
            mid_channels,
            1,
            stride=1,
            conv_cfg=conv_cfg,
            norm_cfg=norm_cfg,
            act_cfg=act_cfg,
        )

        if not split_max_pool_kernel:
            self.poolings = nn.ModuleList(
                [
                    nn.MaxPool2d(kernel_size=ks, stride=1, padding=ks // 2)
                    for ks in kernel_sizes
                ]
            )
        else:
            max_pool_module_list = []
            for ks in kernel_sizes:
                assert (ks - 1) % 2 == 0
                "kernel cannot be splitted into 3x3 kernels"
                num_3x3_maxpool = (ks - 1) // 2
                max_pool_module_list.append(
                    nn.Sequential(
                        *num_3x3_maxpool
                        * [nn.MaxPool2d(kernel_size=3, stride=1, padding=1)]
                    )
                )
            self.poolings = nn.ModuleList(max_pool_module_list)

        conv2_channels = mid_channels * (len(kernel_sizes) + 1)
        self.conv2 = ConvModule(
            conv2_channels,
            out_channels,
            1,
            conv_cfg=conv_cfg,
            norm_cfg=norm_cfg,
            act_cfg=act_cfg,
        )

    def forward(self, x):
        x = self.conv1(x)
        with torch.amp.autocast("cuda", enabled=False):
            x = torch.cat([x] + [pooling(x) for pooling in self.poolings], dim=1)
        x = self.conv2(x)
        return x


class CSPDarknet(BaseModule):
    """CSP-Darknet backbone used in YOLOv5 and YOLOX.

    Args:
        arch (str): Architecture of CSP-Darknet, from {P5, P6}.
            Default: P5.
        deepen_factor (float): Depth multiplier, multiply number of
            blocks in CSP layer by this amount. Default: 1.0.
        widen_factor (float): Width multiplier, multiply number of
            channels in each layer by this amount. Default: 1.0.
        out_indices (Sequence[int]): Output from which stages.
            Default: (2, 3, 4).
        frozen_stages (int): Stages to be frozen (stop grad and set eval
            mode). -1 means not freezing any parameters. Default: -1.
        use_depthwise (bool): Whether to use depthwise separable convolution.
            Default: False.
        arch_ovewrite(list): Overwrite default arch settings. Default: None.
        spp_kernal_sizes: (tuple[int]): Sequential of kernel sizes of SPP
            layers. Default: (5, 9, 13).
        conv_cfg (dict): Config dict for convolution layer. Default: None.
        norm_cfg (dict): Dictionary to construct and config norm layer.
            Default: dict(type='BN', requires_grad=True).
        act_cfg (dict): Config dict for activation layer.
            Default: dict(type='LeakyReLU', negative_slope=0.1).
        norm_eval (bool): Whether to set norm layers to eval mode, namely,
            freeze running stats (mean and var). Note: Effect on Batch Norm
            and its variants only.
        init_cfg (dict or list[dict], optional): Initialization config dict.
            Default: None.
    """

    # From left to right:
    # in_channels, out_channels, num_blocks, add_identity, use_spp
    arch_settings = {
        "P5": [
            [64, 128, 3, True, False],
            [128, 256, 9, True, False],
            [256, 512, 9, True, False],
            [512, 1024, 3, False, True],
        ],
        "P6": [
            [64, 128, 3, True, False],
            [128, 256, 9, True, False],
            [256, 512, 9, True, False],
            [512, 768, 3, True, False],
            [768, 1024, 3, False, True],
        ],
    }

    def __init__(
        self,
        arch="P5",
        deepen_factor=1.0,
        widen_factor=1.0,
        out_indices=(2, 3, 4),
        frozen_stages=-1,
        use_depthwise=False,
        arch_ovewrite=None,
        spp_kernal_sizes=(5, 9, 13),
        conv_cfg=None,
        norm_cfg=dict(type="BN", momentum=0.03, eps=0.001),
        act_cfg=dict(type="Swish"),
        norm_eval=False,
        init_cfg=dict(
            type="Kaiming",
            layer="Conv2d",
            a=math.sqrt(5),
            distribution="uniform",
            mode="fan_in",
            nonlinearity="leaky_relu",
        ),
    ):
        super().__init__(init_cfg)
        arch_setting = self.arch_settings[arch]
        if arch_ovewrite:
            arch_setting = arch_ovewrite
        assert set(out_indices).issubset(i for i in range(len(arch_setting) + 1))
        if frozen_stages not in range(-1, len(arch_setting) + 1):
            raise ValueError(
                "frozen_stages must be in range(-1, "
                "len(arch_setting) + 1). But received "
                f"{frozen_stages}"
            )

        self.out_indices = out_indices
        self.frozen_stages = frozen_stages
        self.use_depthwise = use_depthwise
        self.norm_eval = norm_eval
        conv = DepthwiseSeparableConvModule if use_depthwise else ConvModule

        self.stem = Focus(
            3,
            int(arch_setting[0][0] * widen_factor),
            kernel_size=3,
            conv_cfg=conv_cfg,
            norm_cfg=norm_cfg,
            act_cfg=act_cfg,
        )
        self.layers = ["stem"]

        for i, (
            in_channels,
            out_channels,
            num_blocks,
            add_identity,
            use_spp,
        ) in enumerate(arch_setting):
            in_channels = int(in_channels * widen_factor)
            out_channels = int(out_channels * widen_factor)
            num_blocks = max(round(num_blocks * deepen_factor), 1)
            stage = []
            conv_layer = conv(
                in_channels,
                out_channels,
                3,
                stride=2,
                padding=1,
                conv_cfg=conv_cfg,
                norm_cfg=norm_cfg,
                act_cfg=act_cfg,
            )
            stage.append(conv_layer)
            if use_spp:
                spp = SPPBottleneck(
                    out_channels,
                    out_channels,
                    kernel_sizes=spp_kernal_sizes,
                    conv_cfg=conv_cfg,
                    norm_cfg=norm_cfg,
                    act_cfg=act_cfg,
                )
                stage.append(spp)
            csp_layer = CSPLayer(
                out_channels,
                out_channels,
                num_blocks=num_blocks,
                add_identity=add_identity,
                use_depthwise=use_depthwise,
                conv_cfg=conv_cfg,
                norm_cfg=norm_cfg,
                act_cfg=act_cfg,
            )
            stage.append(csp_layer)
            self.add_module(f"stage{i + 1}", nn.Sequential(*stage))
            self.layers.append(f"stage{i + 1}")

    def _freeze_stages(self):
        if self.frozen_stages >= 0:
            for i in range(self.frozen_stages + 1):
                m = getattr(self, self.layers[i])
                m.eval()
                for param in m.parameters():
                    param.requires_grad = False

    def train(self, mode=True):
        super(CSPDarknet, self).train(mode)
        self._freeze_stages()
        if mode and self.norm_eval:
            for m in self.modules():
                if isinstance(m, _BatchNorm):
                    m.eval()

    def forward(self, x):
        outs = []
        for i, layer_name in enumerate(self.layers):
            layer = getattr(self, layer_name)
            x = layer(x)
            if i in self.out_indices:
                outs.append(x)
        return tuple(outs)
