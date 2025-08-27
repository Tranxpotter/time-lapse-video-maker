import cv2

img = cv2.imread("IMG_9104.JPG")
# print(img.shape)
# print(img.size)
print()
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)