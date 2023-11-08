import PIL.Image as pil
from PIL.ExifTags import TAGS
import glob
import os
import time

# finding metadata of the image


def findMetadata(img_path):
    print("File name: " + img_path)
    img = pil.open(img_path)
    try:
        info = img._getexif()
        for (tag, value) in info.items():
            print(str(TAGS.get(tag, tag)) + " | " + str(value))
    except Exception as e:
        print('Failed to load metadata', e)
    ti_c = os.path.getctime(img_path)
    ti_m = os.path.getmtime(img_path)
    c_ti = time.ctime(ti_c)
    m_ti = time.ctime(ti_m)

    print(
        f"The file located at the path {img_path} was created at {c_ti} and was lsst modified at {m_ti}")
    print("#" * 20)
    print()


pattern = "./exif_samples/*/*"
for img in glob.glob(pattern):
    findMetadata(img)
