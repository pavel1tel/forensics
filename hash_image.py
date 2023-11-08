from PIL import Image
import hashlib

md5hash = hashlib.md5(Image.open('samples/zebra.png').tobytes())
print(md5hash.hexdigest())

sha256hash = hashlib.sha256(Image.open('samples/zebra.png').tobytes())
print(sha256hash.hexdigest()) 