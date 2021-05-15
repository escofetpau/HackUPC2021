from flask import render_template, redirect, make_response
from flask import jsonify, send_file
import os
import torch
from PIL import Image
import operator
import cv2
import numpy
import sys
import time
from numpy import pi

def generate_mapping_data(image_width):
    in_size = [image_width, image_width * 3 / 4]
    edge = in_size[0] / 4  # The length of each edge in pixels
 
    # Create our numpy arrays
    out_pix = numpy.zeros((int(in_size[1]), in_size[0], 2), dtype="f4")
    xyz = numpy.zeros((int(in_size[1] * in_size[0] / 2), 3), dtype="f4")
    vals = numpy.zeros((int(in_size[1] * in_size[0] / 2), 3), dtype="i4")
 
    # Much faster to use an arange when we assign to to vals
    start, end = 0, 0
    rng_1 = numpy.arange(0, edge * 3)
    rng_2 = numpy.arange(edge, edge * 2)
    for i in range(in_size[0]):
        # 0: back
        # 1: left
        # 2: front
        # 3: right
        face = int(i / edge)
        rng = rng_1 if face == 2 else rng_2
 
        end += len(rng)
        vals[start:end, 0] = rng
        vals[start:end, 1] = i
        vals[start:end, 2] = face
        start = end
 
    # Top/bottom are special conditions
    j, i, face = vals.T
    face[j < edge] = 4  # top
    face[j >= 2 * edge] = 5  # bottom
 
    # Convert to image xyz
    a = 2.0 * i / edge
    b = 2.0 * j / edge
    one_arr = numpy.ones(len(a))
    for k in range(6):
        face_idx = face == k
 
        # Using the face_idx version of each is 50% quicker
        one_arr_idx = one_arr[face_idx]
        a_idx = a[face_idx]
        b_idx = b[face_idx]
 
        if k == 0:
           vals_to_use =  [-one_arr_idx, 1.0 - a_idx, 3.0 - b_idx]
        elif k == 1:
           vals_to_use =  [a_idx - 3.0, -one_arr_idx, 3.0 - b_idx]
        elif k == 2:
           vals_to_use =  [one_arr_idx, a_idx - 5.0, 3.0 - b_idx]
        elif k == 3:
           vals_to_use =  [7.0 - a_idx, one_arr_idx, 3.0 - b_idx]
        elif k == 4:
           vals_to_use =  [b_idx - 1.0, a_idx - 5.0, one_arr_idx]
        elif k == 5:
           vals_to_use =  [5.0 - b_idx, a_idx - 5.0, -one_arr_idx]
 
        xyz[face_idx] = numpy.array(vals_to_use).T
 
    # Convert to theta and pi
    x, y, z = xyz.T
    theta = numpy.arctan2(y, x)
    r = numpy.sqrt(x**2 + y**2)
    phi = numpy.arctan2(z, r)
 
    # Source img coords
    uf = (2.0 * edge * (theta + pi) / pi) % in_size[0]
    uf[uf==in_size[0]] = 0.0 # Wrap to pixel 0 (much faster than modulus)
    vf = (2.0 * edge * (pi / 2 - phi) / pi)
 
    # Mapping matrix
    out_pix[j, i, 0] = vf
    out_pix[j, i, 1] = uf
 
    map_x_32 = out_pix[:, :, 1]
    map_y_32 = out_pix[:, :, 0]
    return map_x_32, map_y_32
 

def panorama_to_cubemap(inp_image, out_file='file', out_dir='out'):
    t0 = time.time()
    imgIn = Image.open(inp_image)
    inSize = imgIn.size
    
    map_x_32, map_y_32 = generate_mapping_data(inSize[0])
    cubemap = cv2.remap(numpy.array(imgIn), map_x_32, map_y_32, cv2.INTER_LINEAR)

    imgOut = Image.fromarray(cubemap)
    out_filename = os.path.join(out_dir, f"{out_file}_out1.png") 
    imgOut.save(out_filename)

    # Mateixa foto però una mica rotada
    # h = cubemap.shape[0]
    # w = cubemap.shape[1]
    # left_cols = cubemap[:, 0:int(w/4)].copy()
    # cubemap[:, 0:int(w*3/4)] = cubemap[:, int(w/4):int(w)]
    # cubemap[:, int(w*3/4):int(w)] = left_cols
    # imgOut = Image.fromarray(cubemap)
    # out_filename = os.path.join(out_dir, f"{out_file}_out2.png") 
    # imgOut.save(out_filename)


    # print(time.time() - t0, 'seconds')
    # print('File generated:', out_filename)
    return out_filename

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

def base(request):
    return render_template("index.html", user={'name': 'nico'})


def paint_view(request):
    return render_template("pintar.html")

def photos_names(request, id):
    if id is None or not os.path.isdir(f'static/dataset/{id}'):
        return 'ID does not exist', 400

    photos = os.listdir(f'static/dataset/{id}')
    return jsonify(photos)

def photos_to_text(request, id):
    if id is None or not os.path.isdir(f'static/dataset/{id}'):
        return 'ID does not exist', 400

    if not os.path.exists(f'static/cubemap/{id}'):
        os.mkdir(f'static/cubemap/{id}')
    
    # Weights Rooms
    bathroom = {'toilet':2, 'sink':2}
    bedroom = {'bed':3.5, 'chair':0.5}
    kitchen = {'oven':1, 'sink':0.5, 'refrigerator':1, 'oven':1, 'toaster':0.5}
    diningroom = {'chair':1, 'dining table':3}
    livingroom = {'tv':2, 'couch':2} 
    garage = {'car':4}
    garden = {'potted plant':1, 'bench':3}

    model = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)

    property_rooms = {'bathroom':[], 'bedroom':[], 'kitchen':[], 'diningroom':[], 'livingroom':[], 'garage':[], 'garden':[]}
    photos = os.listdir(f'static/dataset/{id}')

    for photo in photos:
        room = {'bathroom':0, 'bedroom':0, 'kitchen':0, 'diningroom':0, 'livingroom':0, 'garage':0, 'garden':0}

        if not os.path.exists(f'static/cubemap/{id}/{photo[:-5]}_out1.png'):
            panorama_to_cubemap(f'static/dataset/{id}/{photo}', photo[:-5], f'static/cubemap/{id}')

        im = Image.open(f'static/cubemap/{id}/{photo[:-5]}_out1.png')
      
        width, height = im.size
        left = 0
        top = height / 3
        right = width
        bottom = 2 * height / 3
        
        im1 = im.crop((left, top, right, bottom))
        im1.save('static/temp.png')

        results = model('static/temp.png', augment=True)
        items = eval(results.pandas().xyxy[0].to_json(orient="records"))

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
        
        property_rooms[max(room.items(), key=operator.itemgetter(1))[0]].append(elements)

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
            sentences.append('a bed')
            sentences.append('some cupboards')
        if 'tv' in bedroom_elems:
            sentences.append('a tv')
        if 'book' in bedroom_elems:
            sentences.append('some books')
        if 'chair' in bedroom_elems:
            sentences.append('some chairs')

        text += f"This {mockup['type']} has {len(property_rooms['bathroom'])} bathrooms and {len(property_rooms['bedroom'])} bedrooms with {concat_sentences(sentences, False)}.\n"

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

    return text