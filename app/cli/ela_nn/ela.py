import os

import numpy as np
import PIL.Image
import torch
from app.cli.ela_nn.model import IMDModel
from PIL import Image, ImageChops


def infer(img_path, model, device):

    print("Performing Level 2 analysis...")
    ELA(img_path=img_path)

    img = Image.open("temp/ela_img.jpg")
    img = img.resize((128, 128))
    img = np.array(img, dtype=np.float32).transpose(2, 0, 1)/255.0
    img = np.expand_dims(img, axis=0)

    out = model(torch.from_numpy(img).to(device=device))
    y_pred = torch.max(out, dim=1)[1]

    print("Prediction:", end=' ')
    print("Authentic" if y_pred else "Tampared")  # auth -> 1 and tp -> 0


def ELA(img_path):
    DIR = "temp/"
    TEMP = "temp.jpg"
    SCALE = 10
    original = PIL.Image.open(img_path)
    if (os.path.isdir(DIR) == False):
        os.mkdir(DIR)
    original.save(TEMP, quality=90)
    temporary = PIL.Image.open(TEMP)
    diff = ImageChops.difference(original, temporary)
    d = diff.load()
    WIDTH, HEIGHT = diff.size
    for x in range(WIDTH):
        for y in range(HEIGHT):
            d[x, y] = tuple(k * SCALE for k in d[x, y])

    diff.save(DIR+"ela_img.jpg")


def check_ela(path):
    device = torch.device('cuda' if torch.cuda.is_available()
                          else 'cpu')  # selecting device
    print("Working on", device)

    model_path = "model/model_c1.pth"
    model = torch.load(model_path, map_location=torch.device('cpu'))

    infer(model=model, img_path=path, device=device)
