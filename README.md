Hack UPC 2021 - Floorfy Challenge

## Inspiration
Floorfy proposed us this challenge as they want to improve the quality of their tours. They provide us with a lot of 360 images and we thought this challenge fitted us because it involved a lot of terms we were not familiar with like image processing.

## What it does
The platform shows a panoramic view of the tour the user selected. Using the 360 images from each tour, the platform generates automatically a text description of the tour using a Deep Learning model for object detection. Each photo can be edited from the platform to remove the tripod It has at its bottom. 

## How we built it
The main component of the project is a backend developed with Flask. This backend is connected to a frontend (developed with HTML/CSS/JS) and to some services. Those services are connected to a Deep Learning model trained to solve a specific task (object detection or image component removal).

## Challenges we ran into
This is a really big project, time was one of the biggest challenges we have run into, as we only had 36 hours. The treatment of the 360 photos has been very challenging to, as we had to transform each of them into a cubemap. The use of the Deep Learning models was also challenging, as we have never done it before.

## Accomplishments that we're proud of
We adapted those strange photos (360 photos) and used them in two open-source neuronal networks that worked very well. We think this is not an easy process and we managed to obtain good results.

## What we learned
A lot of physics related to 360 images, like how to convert those images into cube maps and vice-versa. We also learned a lot about Deep Learning models, as we have researched a lot on this topic during this hackathon.

## What's next for 360 Image editor for Floorfy
We have more ideas that we haven't had time to build, like a day-night transition for images, to be able to delete any object in the scene (not only the tripod) and adding ambient sound to the tour. We would also like to make some enchantment to the images, we thought this could be done with another DL.


## Requirements
Project edge-connect should be installed in same level as this repo:

```
$ cd wdir
$ git clone https://github.com/escofetpau/HackUPC2021
$ git clone https://github.com/knazeri/edge-connect
```

## Recomended library versions:
Use anaconda enviroment with python 3.6

numpy==1.14.6
scipy==1.0.1
...
