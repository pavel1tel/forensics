import os

import numpy as np
import PIL.Image
import rich
import torch
from PIL import Image, ImageChops

from app.ela_nn.model import IMDModel
from app.utils import get_base_path


def infer(img_path: str, model: IMDModel, device: torch.device) -> None:
    ela(img_path=img_path)

    img = Image.open("temp/ela_img.jpg")
    img = img.resize((128, 128))
    img = np.array(img, dtype=np.float32).transpose(2, 0, 1) / 255.0
    img = np.expand_dims(img, axis=0)

    out = model(torch.from_numpy(img).to(device=device))
    y_pred = torch.max(out, dim=1)[1]

    print("Prediction:", end=" ")
    rich.print("[green]Authentic[/green]" if y_pred else "[red]Tampered[/red]")


def ela(img_path: str) -> None:
    dir_ = "temp/"
    temp = "temp.jpg"
    scale = 10
    original = PIL.Image.open(img_path)
    if not os.path.isdir(dir_):
        os.mkdir(dir_)
    original.save(temp, quality=90)
    temporary = PIL.Image.open(temp)
    diff = ImageChops.difference(original, temporary)
    d = diff.load()
    width, height = diff.size
    for x in range(width):
        for y in range(height):
            d[x, y] = tuple(k * scale for k in d[x, y])

    diff.save(dir_ + "ela_img.jpg")


def check_ela(path: str) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = f"{get_base_path()}/model/model_c1.pth"
    model = torch.load(model_path, map_location=torch.device("cpu"))
    infer(model=model, img_path=path, device=device)
