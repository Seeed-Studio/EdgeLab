import onnxruntime
import torch

from .base_infer import BaseInfer


class OnnxInfer(BaseInfer):
    def __init__(self, weights="sscma.onnx", device=torch.device("cpu")):
        super().__init__(weights=weights, device=device)
        self.output_names = None
        self.input_name = None
        self.sess = None

    def infer(self, input_data, split=True):
        results = []
        if split:
            for data in input_data.split(1, 0):
                # check if input_data is Tensor
                if isinstance(data, torch.Tensor):
                    data = data.numpy()
                results.append(
                    self.sess.run(self.output_names, {self.input_name: data})
                )
        else:
            # check if input_data is Tensor
            if isinstance(input_data, torch.Tensor):
                input_data = input_data.numpy()
            results = self.sess.run(self.output_names, {self.input_name: input_data})
        return results

    def load_weights(self):
        self.sess = onnxruntime.InferenceSession(
            self.weights,
            providers=[
                "TensorrtExecutionProvider",
                "CUDAExecutionProvider",
                "CPUExecutionProvider",
            ],
        )
        self.input_name = self.sess.get_inputs()[0].name
        self.output_names = [x.name for x in self.sess.get_outputs()]
