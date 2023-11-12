import os

import cv2

# read image
img1 = cv2.imread("samples/zebra.png")

# set compression and scale
jpg_quality1 = 95
jpg_quality2 = 90
scale = 25

# create output folder
os.makedirs("out")

# write img1 at 95% jpg compression
cv2.imwrite("out/c95.jpg", img1, [cv2.IMWRITE_JPEG_QUALITY, jpg_quality1])

# read compressed image
img2 = cv2.imread("out/c95.jpg")

# get absolute difference between img1 and img2 and multiply by scale
diff1 = scale * cv2.absdiff(img1, img2)

# write img2 at 90% jpg compression
cv2.imwrite("out/c90.jpg", img2, [cv2.IMWRITE_JPEG_QUALITY, jpg_quality2])

# read compressed image
img3 = cv2.imread("out/c90.jpg")

# get absolute difference between img1 and img2 and multiply by scale
diff2 = scale * cv2.absdiff(img2, img3)

# write result to disk
cv2.imwrite("out/ela_95.jpg", diff1)
cv2.imwrite("out/ela_90.jpg", diff2)

# display it
cv2.imshow("ela95", diff1)
cv2.imshow("ela90", diff2)
cv2.waitKey(0)
