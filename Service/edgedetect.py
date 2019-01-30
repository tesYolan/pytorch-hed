import torch
# import torch.utils.serialization

import getopt
import math
import numpy
import os
import PIL
import PIL.Image
import sys
import base64

from inspect import getsourcefile
import os.path
import sys
import io
import tempfile

current_path = os.path.abspath(getsourcefile(lambda: 0))
current_dir = os.path.dirname(current_path)
parent_dir = current_dir[:current_dir.rfind(os.path.sep)]

sys.path.insert(0, parent_dir)

from hed import Network, estimate

train_on_gpu = torch.cuda.is_available()


def detectedge(image_in, image_type):
    IMAGE_TYPE = image_type
    binary_image = base64.b64decode(image_in).decode('utf-8')
    f = tempfile.NamedTemporaryFile()
    f.write(binary_image)
    if image_type == 'RGB':
        image = PIL.Image.Open(f.name)
        # =image_in, size=(480, 320), mode='RGB')
    else:
        image = PIL.Image.Open(f.name)
        image = image.convert('RGB')
        IMAGE_TYPE = 'L'

    if train_on_gpu:
        moduleNetwork = Network().cuda().eval()
    else:
        moduleNetwork = Network().eval()

    img_array = numpy.array(image)
    tensorInput = torch.FloatTensor(img_array[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0))
    tensorOutput = estimate(tensorInput, moduleNetwork)
    img_out = PIL.Image.fromarray((tensorOutput.clamp(0.0, 1.0).detach().numpy().transpose(1, 2, 0)[:, :, 0] * 255.0))

    img = base64.b64encode(img_out.convert(IMAGE_TYPE).tobytes()).decode('utf-8')
    return img
