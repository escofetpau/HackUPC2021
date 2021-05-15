import torch
import pickle
import time

# start = time.time()
# model = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)
# print(time.time() - start, 's')

# with open('yolo.pickle', 'wb') as file:
#   pickle.dump(model, file, protocol=pickle.HIGHEST_PROTOCOL)

start = time.time()
with open('yolo.pickle', 'rb') as file:
  b = pickle.load(file)
print(time.time() - start, 's')


results = b('kitchen.png')
results.show()