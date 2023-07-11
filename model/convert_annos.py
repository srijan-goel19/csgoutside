import os
import glob
import json
import pandas as pd
import numpy as np
import cv2
import shutil
directory_annos = r'C:\FASHION_DSET\validation\annos'
directory_images = r'C:\FASHION_DSET\validation\image'
files_list = glob.glob(os.path.join(directory_annos, '*.json'))
images_list = glob.glob(os.path.join(directory_images, '*.jpg'))

allowed_cids = [1, 2, 3, 4, 5]

# CODE TO CONVERT DF ANNOS TO YOLO ANNOS
images = {}

for image_fp in images_list[1500:1700]:
    im_sh = cv2.imread(image_fp).shape
    num = os.path.basename(image_fp[0:len(image_fp)-4])
    images[num] = (im_sh[1], im_sh[0])

print("done")

printOut = 0
for fp in files_list[1500:1700]:

    with open(fp, 'r') as f:

        annos = json.load(f)
        num = os.path.basename(fp[0:len(fp)-5])
        image_df = pd.DataFrame(
            columns=['class_id', 'x_center', 'y_center', 'width', 'height'])

        for key in annos.keys():
            if key != 'source' and key != 'pair_id':
                if annos[key]['category_id'] in allowed_cids:
                    printOut = 1

                    class_id = annos[key]['category_id']-1
                    bbox = annos[key]['bounding_box']

                    width = (bbox[2]-bbox[0])
                    height = (bbox[3]-bbox[1])

                    dw, dh = images[num]

                    x_center = (bbox[0] + bbox[2])/2.0
                    y_center = (bbox[1] + bbox[3])/2.0

                    x_center = (1.0/dw)*x_center
                    y_center = (1.0/dh)*y_center

                    width = (1.0/dw)*width
                    height = (1.0/dh)*height

                    image_df.loc[len(image_df)] = [
                        class_id, x_center, y_center, width, height]

        if printOut == 1:
            np.savetxt(r'C:\Small_dset\test\labels\\'+num+r'.txt',
                       image_df.values, fmt=['%d', '%f', '%f', '%f', '%f'])
        printOut = 0

print("done creating txt label files")
# annos_yolo_list = glob.glob(os.path.join(
#     r'C:\FASHION_DSET\validation\annos_yolo', '*.txt'))
# print(len(annos_yolo_list))


# image_path = r'C:\FASHION_DSET\train\image\000384'
# og_anno_path = r'C:\FASHION_DSET\train\annos\000384.json'
# # CODE TO TEST WHETHER YOLO BOUNDING BOXES ARE CORRECT
# og_bbox = []
# with open(og_anno_path, 'r') as f:
#     annos = json.load(f)
#     for key in annos.keys():
#         if key != 'source' and key != 'pair_id':
#             if annos[key]['category_id'] in allowed_cids:
#                 og_bbox = annos[key]['bounding_box']

# image = cv2.imread(image_path + '.jpg')

# class_list = ['short_top', 'long_top', 'short_outwear', 'long_outwear', 'vest']
# colors = [(0, 255, 0), (0, 255, 255), (0, 0, 0), (255, 0, 0), (255, 255, 0)]

# height, width, _ = image.shape

# T = []
# with open(r'C:\FASHION_DSET\train\annos_yolo\000384' + '.txt', "r") as file1:
#     for line in file1.readlines():
#         split = line.split(" ")

#         # getting the class id
#         class_id = int(split[0])
#         color = colors[class_id]

#         # getting the xywh bounding box coordinates
#         x, y, w, h = float(split[1]), float(
#             split[2]), float(split[3]), float(split[4])

#         print(x, y, w, h)
#         # re-scaling xywh to the image size
#         # box = [int((x - 0.5*w) * width), int((y - 0.5*h) * height),
#         #        int(w*width), int(h*height)]

#         box = [int(x*width - 0.5*w), int(y*height - 0.5*h),
#                int(x*width + 0.5*w), int(y*height + 0.5*h)]
#         cv2.rectangle(image, box, (0, 255, 255), 2)
#         cv2.rectangle(image, (box[0], box[1] - 20),
#                       (box[0] + box[2], box[1]), (0, 255, 255), -1)
#         cv2.putText(image, class_list[class_id], (box[0],
#                     box[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0))

# cv2.imshow("output", image)
# cv2.waitKey()


directory_annos_yolo = glob.glob(os.path.join(
    r'C:\Small_dset\test\labels', '*.txt'))

# yolo_image_nums = []

for file in directory_annos_yolo:
    num = os.path.basename(file[0:len(file)-4])
    shutil.copyfile(r'C:\FASHION_DSET\validation\image\\'+num+'.jpg',
                    r'C:\Small_dset\test\images\\'+num+'.jpg')

print("done copying relevant images")
