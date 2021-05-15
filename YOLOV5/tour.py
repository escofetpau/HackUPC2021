# https://pypi.org/project/yolov5/
# https://colab.research.google.com/github/pytorch/pytorch.github.io/blob/master/assets/hub/ultralytics_yolov5.ipynb#scrollTo=2TIP-Omi45MF

import torch
from pprint import pprint
from PIL import Image
import operator

def concat_sentences(sentences, add_be = True):
  if len(sentences) == 0:
    return "nothing"

  text = ""

  if add_be:
    if sentences[0].split(' ')[0] == 'some':
      text += 'are '
    else:
      text += 'is '

  for s in sentences[:-1]:
    text += s
    if s == sentences[-2]:
      text += ' and '
    else:
      text += ', '

  text += sentences[-1]

  return text


####### Rooms
bathroom = {'toilet':2, 'sink':2}
bedroom = {'bed':3.5, 'chair':0.5}
kitchen = {'oven':1, 'sink':0.5, 'refrigerator':1, 'oven':1, 'toaster':0.5}
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
# images = [19, 20, 21, 29, 33, 34, 35]

# tour_name = '426870'
# images = [str(i) for i in range(7)]

random_objects = {'chair', 'tv', 'couch', 'potted plant'}

with open(f"{tour_name}/{tour_name}.txt", 'w') as file:

  # model
  model = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)

  property_rooms = {'bathroom':[], 'bedroom':[], 'kitchen':[], 'diningroom':[], 'livingroom':[], 'garage':[], 'garden':[]}

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

    elements = []

    for item in items:
      elements.append(item['name'])

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

    property_rooms[max(room.items(), key=operator.itemgetter(1))[0]].append(elements)

    # show results
    # results.show()

  # save results
  # results.save(save_dir='results/')
  pprint(property_rooms)

### Generació del text
mockup = {'type': 'house', 'city': 'Barcelona', 'street': 'Rambla'}

text = ""

# Type and location
text += f"This property is a {mockup['type']} located in {mockup['city']} on street {mockup['street']}.\n"

# Bathroom and bedrooms
bedroom_elems = set()
for i in property_rooms['bedroom']:
  bedroom_elems = bedroom_elems.union(set(i))

sentences = []
if 'bed' in bedroom_elems:
  sentences.append('a bed, some cupboards')
if 'tv' in bedroom_elems:
  sentences.append('a tv')
if 'book' in bedroom_elems:
  sentences.append('some books')
if 'chair' in bedroom_elems:
  sentences.append('some chairs')
text += f"This {mockup['type']} has {len(property_rooms['bathroom'])} bathrooms and {len(property_rooms['bedroom'])} bedrooms with {concat_sentences(sentences, False)}\n"

# Diningroom
diningroom_elems = set()
for i in property_rooms['diningroom']:
  diningroom_elems = diningroom_elems.union(set(i))

sentences = []
if 'couch' in diningroom_elems:
  sentences.append('a couch')
if 'chair' in diningroom_elems:
  sentences.append('some chairs')
if 'tv' in diningroom_elems:
  sentences.append('a tv')
if 'potted plant' in diningroom_elems:
  sentences.append('some potted plants')
if 'dining table' in diningroom_elems:
  sentences.append('a dining table')

if len(sentences) != 0:
  text += f"In the dining room there {concat_sentences(sentences)}."

# Kitchen
kitchen_elems = set()
for i in property_rooms['kitchen']:
  kitchen_elems = kitchen_elems.union(set(i))

sentences = []
if 'oven' in kitchen_elems:
  sentences.append('an oven')
if 'refrigerator' in kitchen_elems:
  sentences.append('a refrigerator')
if 'sink' in kitchen_elems:
  sentences.append('a sink')
if 'microwave' in kitchen_elems:
  sentences.append('a microwave')
if 'toaster' in kitchen_elems:
  sentences.append('a toaster')
if 'chair' in kitchen_elems:
  sentences.append('some chairs')

if len(sentences) != 0:
  text += f" Regarding the kitchen there {concat_sentences(sentences)}."

# Livingroom
livingroom_elems = set()
for i in property_rooms['livingroom']:
  livingroom_elems = livingroom_elems.union(set(i))

sentences = []
if 'couch' in livingroom_elems:
  sentences.append('a couch')
if 'tv' in livingroom_elems:
  sentences.append('a tv')
if 'potted plant' in livingroom_elems:
  sentences.append('some potted plants')
if 'chair' in livingroom_elems:
  sentences.append('some chairs')

if len(sentences) != 0:
  text += f" In the livingroom there {concat_sentences(sentences)}."

# Garden
garden_elems = set()
for i in property_rooms['garden']:
  garden_elems = garden_elems.union(set(i))

sentences = []
if 'potted plant' in garden_elems:
  sentences.append('some plotted plants')
if 'chair' in garden_elems:
  sentences.append('some chairs')
if 'bench' in garden_elems:
  sentences.append('a bench')
if 'fence' in garden_elems:
  sentences.append('a fence')
if 'couch' in garden_elems:
  sentences.append('a couch')
if 'vase' in garden_elems:
  sentences.append('some vase')

if len(sentences) != 0:
  text += f" The property also has a garden with {concat_sentences(sentences)}."

#TODO: garage??

print(text)