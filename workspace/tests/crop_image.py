from PIL import Image

img = Image.open('storage/cam_photos/STC-MBS500U3V(22K5341)0.png')
img.show()

box = (231, 1, 611, 705)
img2 = img.crop(box)

img2.show()
