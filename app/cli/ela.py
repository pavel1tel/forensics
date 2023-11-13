import os

import cv2

JPG_QUALITY1 = 95
JPG_QUALITY2 = 90
SCALE = 25


def generate_ela(path: str) -> None:
    img1 = cv2.imread(path)
    name = path.split("/")[-1]

    if not os.path.exists("out"):
        os.makedirs("out")

    cv2.imwrite(f"out/{name}_c95.jpg", img1, [cv2.IMWRITE_JPEG_QUALITY, JPG_QUALITY1])

    img2 = cv2.imread(f"out/{name}_c95.jpg")

    diff1 = SCALE * cv2.absdiff(img1, img2)

    cv2.imwrite(f"out/{name}_c90.jpg", img2, [cv2.IMWRITE_JPEG_QUALITY, JPG_QUALITY2])

    img3 = cv2.imread(f"out/{name}_c90.jpg")

    diff2 = SCALE * cv2.absdiff(img2, img3)

    cv2.imwrite(f"out/{name}_ela_95.jpg", diff1)
    cv2.imwrite(f"out/{name}_ela_90.jpg", diff2)
