import cv2
import numpy
import sys
import os
import time

from numpy import pi
from PIL import Image
 
# Convert using an inverse transformation
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
 

def panorama_to_cubemap(inp_image):
    t0 = time.time()
    imgIn = Image.open(inp_image)
    inSize = imgIn.size
    
    map_x_32, map_y_32 = generate_mapping_data(inSize[0])
    cubemap = cv2.remap(numpy.array(imgIn), map_x_32, map_y_32, cv2.INTER_LINEAR)
    
    imgOut = Image.fromarray(cubemap)
    out_filename = inp_image.split('/')[-1].split('.')[0]+"_out.png" 
    imgOut.save(out_filename)
    print(time.time() - t0, 'seconds')
    print('File generated:', out_filename)
    return out_filename


def files_to_panorama(front, back, right, left, top, bottom):
    t0 = time.time()

    output_filename = f'{int(time.time())}'
    command = f'cube2sphere {front} {back} {right} {left} {top} {bottom} -f PNG -o {output_filename}'
    os.system(command)

    print(time.time() - t0, 'seconds')
    print(f'File generated: {output_filename}.png')

    return output_filename


def show_im(image):
    cv2.imshow('shit', image)
    cv2.waitKey()

def cubemap_to_6_files(fname):
    file_name = fname.split('/')[-1].split('.')[0]
    image = cv2.imread(fname)
    h = image.shape[0]
    w = image.shape[1]
    
    back    = image[int(h/3):int(h*2/3), 0:int(w/4)]
    left    = image[int(h/3):int(h*2/3), int(w/4):int(w*2/4)]
    front   = image[int(h/3):int(h*2/3), int(w*2/4):int(w*3/4)]
    right   = image[int(h/3):int(h*2/3), int(w*3/4):int(w)]
    top     = image[0:int(h/3), int(w*2/4):int(w*3/4)]
    bottom  = image[int(h*2/3):int(h), int(w*2/4):int(w*3/4)]

    cv2.imwrite('back.png', back)
    cv2.imwrite('left.png', left)
    cv2.imwrite('front.png', front)
    cv2.imwrite('right.png', right)
    cv2.imwrite('top.png', top)
    cv2.imwrite('bottom.png', bottom)


if __name__ == "__main__":
    fname = 'tours_1/905/l_r_equirectangular_905_59bf9b6637fd6.jpeg'

    # panorama_to_cubemap(fname)

    cubemap_to_6_files('prova_out.png')
    files_to_panorama('back.png', 'front.png', 'right.png','left.png', 'top.png', 'bottom.png')