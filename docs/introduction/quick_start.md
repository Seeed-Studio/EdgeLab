# Quick Start

In [Overview](./what_is_edgelab), we have introduced the functions and features provided by EdgeLab. Considering that EdgeLab is divided into multiple different modules, each module completing its corresponding tasks, we suggest following the steps below to quickly get started.

::: tip
We suggest that all beginners of EdgeLab start learning from [Getting Started](#getting-started), if you are familiar with EdgeLab or [OpenMMLab](https://github.com/open-mmlab), and you want to try to deploy on edge computing devices, modify existing neural networks, or train on user-defined data sets, you can directly refer to [Advanced](#advanced).
:::

Now, you can try out [EdgeLab Colab Examples](https://github.com/Seeed-Studio/EdgeLab/tree/main/notebooks) on Google Colab without setup EdgeLab on your computer.

## Getting Started

1. First, refer to the [Installation Guide](./installation.md) to configure the running environment of EdgeLab.

2. Then, familiar with the basic usage methods of EdgeLab:

   - **Model Training**, please refer to [Model Training](../tutorials/training/overview) to learn how to use EdgeLab to train a model. We suggest that you select a model from an example for training.

   - **Model Export**. After completing model training, in order to deploy on the edge-computing device, it is necessary to first export the model. For the export tutorial of the model, please refer to [Model Export](../tutorials/export/overview).

   - **Model Verification**. Model verification can be performed after training or export. The former verifies the correctness of the neural network and training results, while the latter mainly verifies the correctness of the exported model, facilitating deployment and debugging on edge computing devices later. Some methods for model validation have been provided in the documents in the above two steps.

## Advanced

- **Model Deployment**. If you want to deploy the exported training model on edge computing devices, please refer to [ESP32 Deployment Example](../deploy/esp32/deploy) or [Grove Vision AI Deployment Example](../deploy/grove/deploy).

- **Custom Datasets**. If you want to train on a custom dataset, please refer to [Datasets](../tutorials/datasets).

- **Custom Model**. If you want to modify an existing neural network or design your own neural network, please refer to [Model Configuration](../tutorials/config).

## Necessary Knowledge

- Computer Vision:

  The basics of computer vision are built upon digital image processing. So, you need to learn the basics of the DlP first. Then you can move forward to read computer vision topics like pattern recognition and 3D geometry. You need to know linear algebra to be able to fully understand some concepts of the computer vision like dimensionality reduction. After understanding the fundamentals of computer vision you should also build your knowledge in deep learning, especially in Convolutional Neural Networks (CNN).

- Programming:

  Python will be enough for design and prototyping, but if you want to do some
  embedded work, you should also be familiar with C++.

- Tools:

  OpenCV is the main tool for computer vision, and Numpy is an important tool for data processing and analysis. You must know them. You never know, but you should know what tools are available and how to use them. How to use them. Another tool you need to familiarize yourself with is the deep learning framework. Frameworks. You can start with Keras which is the easiest to learn and then learn Tensorflow or PyTorch.
