# https://pypi.org/project/yolov5/
# https://colab.research.google.com/github/pytorch/pytorch.github.io/blob/master/assets/hub/ultralytics_yolov5.ipynb#scrollTo=2TIP-Omi45MF

import torch
from pprint import pprint
from PIL import Image

image_name = 'bedroom'

im = Image.open(f'{image_name}.png')
  
width, height = im.size
  

left = 0
top = height / 3
right = width
bottom = 2 * height / 3
  
im1 = im.crop((left, top, right, bottom))
  
im1.save('temp.png')

# model
model = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)

# inference with test time augmentation
results = model('temp.png', augment=True)

results.print()
pprint(eval(results.pandas().xyxy[0].to_json(orient="records")))

# show results
results.show()

# save results
# results.save(save_dir='results/')