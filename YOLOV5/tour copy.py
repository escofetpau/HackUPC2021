# https://pypi.org/project/yolov5/
# https://colab.research.google.com/github/pytorch/pytorch.github.io/blob/master/assets/hub/ultralytics_yolov5.ipynb#scrollTo=2TIP-Omi45MF

import torch
from pprint import pprint
from PIL import Image
import operator

####### Rooms
bathroom = {'toilet':2, 'sink':2}
bedroom = {'bed':3.5, 'chair':0.5}
kitchen = {'oven':1, 'sink':1, 'refrigerator':1, 'oven':1}
diningroom = {'chair':1, 'dining table':3}
livingroom = {'tv':2, 'couch':2} 
garage = {'car':4}
garden = {'potted plant':1, 'bench':3}

# tour_name = '427083'
# images = [str(i) for i in range(8)]

# tour_name = '814'
# images = [str(i) for i in range(12)]

tour_name = '916'
images = [0, 11, 13, 17, 19, 20, 21, 29, 33, 34, 35, 36, 38, 42]

# tour_name = '426870'
# images = [str(i) for i in range(7)]

with open(f"{tour_name}/{tour_name}.txt", 'w') as file:

  # model
  model = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)

  for image in images:
    im = Image.open(f'{tour_name}/{image}_out1.png')
      
    width, height = im.size
      
    left = 0
    top = height / 3
    right = width
    bottom = 2 * height / 3
      
    im1 = im.crop((left, top, right, bottom))
      
    im1.save('temp.png')

    # inference with test time augmentation
    results = model('temp.png', augment=True)

    results.print()
    items = eval(results.pandas().xyxy[0].to_json(orient="records"))

    room = {'bathroom':0, 'bedroom':0, 'kitchen':0, 'diningroom':0, 'livingroom':0, 'garage':0, 'garden':0}
    file.write(f'\nImage: {image}')

    for item in items:
      if item['name'] in bathroom:
        room['bathroom'] += item['confidence']*bathroom[item['name']]

      if item['name'] in bedroom:
        room['bedroom'] += item['confidence']*bedroom[item['name']]

      if item['name'] in kitchen:
        room['kitchen'] += item['confidence']*kitchen[item['name']]

      if item['name'] in diningroom:
        room['diningroom'] += item['confidence']*diningroom[item['name']]

      if item['name'] in livingroom:
        room['livingroom'] += item['confidence']*livingroom[item['name']]

      if item['name'] in garage:
        room['garage'] += item['confidence']*garage[item['name']]

      if item['name'] in garden:
        room['garden'] += item['confidence']*garden[item['name']]

      file.write(f"\n{item['name']} ({item['confidence']})")
      

    file.write(f'\n{str(room)}\n')
    file.write(f'{max(room.items(), key=operator.itemgetter(1))[0]}\n')

    # show results
    # results.show()

  # save results
  # results.save(save_dir='results/')