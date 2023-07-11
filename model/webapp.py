# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
"""
Run a Flask REST API exposing one or more YOLOv5s models
"""
from pathlib import Path
import argparse
import io
import math
import cv2
import torch
from flask import Flask, request
from PIL import Image
import websocket, json
import base64
import numpy as np
import os, glob

app = Flask(__name__)
model = None

DETECTION_URL = "/predict"
REGISTER_URL = "/register"


def on_message(ws, message):
    msg = json.loads(message)

    # if msg["reset"] == "reset":
    #     register_dir = glob.glob(os.path.join(r"C:\model\register", "*.jpg"))

    #     print(register_dir)
    #     for fp in register_dir:
    #         print("removed")
    #         os.remove(fp)

    method = msg["ml_method"]
    user_id = msg["user_id"]

    if method == "user":
        # register

        encoded_data = msg["shirt"].split(",")[1]
        img = Image.open(io.BytesIO(base64.b64decode(encoded_data)))

        results = model(img, size=640)  # reduce size=320 for faster inference
        crop = results.crop(save=False)

        # cv2.imwrite(
        #     r"C:\model\register\\" + str(user_id) + r".jpg", results[0]["im"]
        # )

        # img = cv2.imread(r"C:\model\register\\" + str(user_id) + r".jpg")

        crop_img = crop[0]["im"]
        h, w, _ = crop_img.shape

        [x1, y1, x2, y2] = get_corners(h, w)

        # img = (img[y1:y2, x1:x2]).reshape(-1, 3)

        # print(img)

        cv2.imwrite(
            r"C:\model\register\\" + str(user_id) + r".jpg", crop_img[y1:y2, x1:x2]
        )

        # lower, upper = get_color_range(img)

        # obj = {"user_id": user_id, "lower": lower, "upper": upper}
        # file_name = r"C:\model\colors\\" + str(user_id) + r".txt"
        # with open(file_name, "w") as f:
        #     json.dump(obj, f)

        print("registered  image")

        ws.send(json.dumps({"id": "bababooey", "status": "registered"}))
    else:
        # shot

        # decode base64

        encoded_data = msg["playerShot"].split(",")[1]
        img = Image.open(io.BytesIO(base64.b64decode(encoded_data)))

        # pass the image through model for inference

        results = model(img, size=640)

        crop = results.crop(save=False)

        bounding_boxes = []

        for hit in crop:
            box = [tensor.item() for tensor in hit["box"]]
            bounding_boxes.append(box)

        # img = cv2.imread(r"C:\model\register\6435e2d04ee8e2528a60202f.jpg")
        img = cv2.cvtColor(results.render()[0], cv2.COLOR_BGR2RGB)
        h, w, _ = img.shape

        [x1, y1, x2, y2] = get_corners(h, w)
        ch = [x1, y1, x2, y2]

        accepted_bb = {}
        count = 0

        for bb in bounding_boxes:
            if (bb[0] < x2 and bb[2] > x1) and (bb[1] < y2 and bb[3] > y1):
                accepted_bb[count] = bb

            count += 1

        key = list(accepted_bb.keys())[0]

        crop_img = crop[key]["im"]
        h, w, _ = crop_img.shape
        central_coords = get_corners(h, w)

        cv2.imwrite(
            r"C:\model\crops\\" + str(user_id) + r".jpg",
            crop_img[
                central_coords[1] : central_coords[3],
                central_coords[0] : central_coords[2],
            ],
        )

        intersection = box_intersection(ch, accepted_bb[key])

        percent = (
            (intersection[3] - intersection[1]) * (intersection[2] - intersection[0])
        ) / ((ch[3] - ch[1]) * (ch[2] - ch[0]))
        dmg = 0.5 * percent * 100
        print(0.5 * percent * 100)
        # print((intersection[2] - intersection[1]) * (intersection[3] - intersection[0]))

        start_point = (x1, y1)  # clear x, y
        end_point = (x2, y2)  # x, y
        color = (0, 0, 0)  # B, G, R
        thickness = 2  # Line thickness (pixels)

        # Draw rectangle on image
        cv2.rectangle(img, start_point, end_point, color, thickness)

        #  img = cv2.imread(results.render())

        # code to display
        # cv2.startWindowThread()
        # cv2.namedWindow("preview", cv2.WINDOW_NORMAL)
        ims = cv2.resize(img, (640, 640))
        cv2.imwrite(r"C:\model\shots\\" + str(user_id) + r".jpg", ims)
        # cv2.imshow("preview", ims)
        # cv2.waitKey()

        # final prediction of who got shot:

        all_players = glob.glob(os.path.join(r"C:\model\register", "*.jpg"))
        # crop_check = cv2.cvtColor(
        #     crop_img[
        #         central_coords[1] : central_coords[3],
        #         central_coords[0] : central_coords[2],
        #     ],
        #     cv2.COLOR_RGB2HSV,
        # )

        crop_img = cv2.imread(r"C:\model\crops\\" + str(user_id) + r".jpg")

        victim_id = None
        min = 256.0
        for player in all_players:
            im_player = cv2.imread(player)

            reds = crop_img[:, :, 2].flatten()
            greens = crop_img[:, :, 1].flatten()
            blues = crop_img[:, :, 0].flatten()

            red_shot_avg = np.sum(reds) / reds.shape[0]
            green_shot_avg = np.sum(greens) / greens.shape[0]
            blues_shot_avg = np.sum(blues) / blues.shape[0]

            reds_p = im_player[:, :, 2].flatten()
            greens_p = im_player[:, :, 1].flatten()
            blues_p = im_player[:, :, 0].flatten()

            reds_p_avg = np.sum(reds_p) / reds_p.shape[0]
            green_p_avg = np.sum(greens_p) / greens_p.shape[0]
            blues_p_avg = np.sum(blues_p) / blues_p.shape[0]

            targ_coords = np.array([red_shot_avg, green_shot_avg, blues_shot_avg])
            player_coords = np.array([reds_p_avg, green_p_avg, blues_p_avg])

            print(player, np.linalg.norm(player_coords - targ_coords))
            dist = np.linalg.norm(player_coords - targ_coords)
            if dist < min and dist <= 70.0 and Path(player).stem != user_id:
                min = dist
                victim_id = Path(player).stem

        os.remove(r"C:\model\crops\\" + str(user_id) + r".jpg")

        if victim_id != None:
            response = {
                "id": "shot_response",
                "shooter_id": user_id,
                "victim_id": victim_id,
                "damage": dmg,
            }

            print(response)

            ws.send(json.dumps(response))
    # else:
    # register_dir = glob.glob(os.path.join(r"C:\model\register", "*.jpg"))
    # print(method)
    # print(register_dir)
    # for fp in register_dir:
    #     print("removed")
    #     os.remove(fp)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print(close_status_code)
    print("### closed ###")


def on_open(ws):
    print("Opened connection")
    message = {"id": "greeting", "content": "Hello, server!"}
    ws.send(json.dumps(message))


@app.route(DETECTION_URL, methods=["POST"])
def predict():
    if request.method != "POST":
        return

    if request.files.get("image"):
        # Method 1
        # with request.files["image"] as f:
        #     im = Image.open(io.BytesIO(f.read()))

        # Method 2
        im_file = request.files["image"]
        im_bytes = im_file.read()
        im = Image.open(io.BytesIO(im_bytes))

        results = model(im, size=640)  # reduce size=320 for faster inference
        return results.pandas().xyxy[0].to_json(orient="records")


@app.route(REGISTER_URL, methods=["POST"])
def register():
    if request.method != "POST":
        return

    if request.files.get("image"):
        # Method 1
        # with request.files["image"] as f:
        #     im = Image.open(io.BytesIO(f.read()))

        # Method 2
        im_file = request.files["image"]
        im_bytes = im_file.read()
        im = Image.open(io.BytesIO(im_bytes))

        results = model(im, size=640)  # reduce size=320 for faster inference
        results = results.crop(save=False)
        results.render()

        img = cv2.cvtColor(results.ims[0], cv2.COLOR_RGB2BGR)
        cv2.imshow("name", img)
        user_id = 1234
        print(results.ims[0])

        cv2.imwrite(
            r"C:\model\results\\" + str(user_id) + r".jpg",
            cv2.cvtColor(results.ims[0], cv2.COLOR_RGB2BGR),
        )
        # waits for user to press any key
        # (this is necessary to avoid Python kernel form crashing)
        #        cv2.waitKey(0)

        # closing all open windows
        #        cv2.destroyAllWindows()
        return results.pandas().xyxy[0].to_json(orient="records")


def get_corners(h, w):
    x = math.sqrt(0.05 * h * w)
    y1 = int(0.5 * (h - x))
    y2 = int(0.5 * (h + x))
    x1 = int(0.5 * (w - x))
    x2 = int(0.5 * (w + x))
    return [x1, y1, x2, y2]


def box_intersection(box1, box2):
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    return [x_left, y_top, x_right, y_bottom]


def get_color_range(img):
    reds = [i[2] for i in img]
    greens = [i[1] for i in img]
    blues = [i[0] for i in img]

    rmin, gmin, bmin = int(min(reds)), int(min(greens)), int(min(blues))
    rmax, gmax, bmax = int(max(reds)), int(max(greens)), int(max(blues))

    lower = [bmin, gmin, rmin]
    upper = [bmax, gmax, rmax]

    return lower, upper


def get_color_diff(img1, img2):
    print(type(img1))
    print(type(img2))
    lower, upper = get_color_range(img2)
    print(lower, upper)
    mask = cv2.inRange(img1, lower, upper)
    mask = mask.reshape(1, -1)[0]
    hits = [i for i in mask if i != 0]
    (len(hits) / len(mask)) * 100
    # img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HLS)
    # img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HLS)

    # h1, w1, _ = img1.shape
    # h2, w2, _ = img2.shape

    # final_h = min(h1, h2)
    # final_w = min(w1, w2)

    # img1 = cv2.resize(img1, (final_w, final_h))
    # img2 = cv2.resize(img2, (final_w, final_h))

    # for x in range(img1.shape[0]):
    #     for y in range(img1.shape[1]):
    #         rgb1 = img1[x,y]
    #         rgb2 = img2[x,y]
    #         hsl1 = rgb_to_hsl(rgb1)
    #         hsl2 = rgb_to_hsl(rgb2)
    #         diff += abs(hsl1[0] - hsl2[0])
    #         diff += abs(hsl1[1] - hsl2[1])
    #         diff += abs(hsl1[2] - hsl2[2])
    # return diff / (img1.shape[0] * img1.shape[1])

    # reds1 = [i[0] for i in img1]
    # greens1 = [i[1] for i in img1]
    # blues1 = [i[2] for i in img1]

    # reds2 = [i[0] for i in img2]
    # greens2 = [i[1] for i in img2]
    # blues2 = [i[2] for i in img2]

    # diffRed = []
    # diffBlue = []
    # diffGreen = []

    # for i in range(len(reds1)):
    #     diffRed.append(abs(reds2[i] - reds1[i]))
    #     diffGreen.append(abs(greens2[i] - greens1[i]))
    #     diffBlue.append(abs(blues2[i] - blues1[i]))

    # diffRed = np.array(diffRed)
    # diffBlue = np.array(diffBlue)
    # diffGreen = np.array(diffGreen)

    # pctDiffRed = np.divide(diffRed, 255.0)
    # pctDiffGreen = np.divide(diffGreen, 255.0)
    # pctDiffBlue = np.divide(diffBlue, 255.0)
    # pctDiffGreen = [(float(i) / 255) for i in diffGreen]
    # pctDiffBlue = [(float(i) / 255) for i in diffBlue]

    # redavg = np.sum(pctDiffRed)
    # greenavg = np.sum(pctDiffGreen)
    # blueavg = np.sum(pctDiffBlue)

    # diffavg = float(redavg + blueavg + greenavg) / 3
    # return diffavg


if __name__ == "__main__":
    model = torch.hub.load(
        r"C:\model\yolov5",
        "custom",
        path=r"C:\model\yolov5\runs\train\exp\weights\best.pt",
        source="local",
    )  # local repo

    ws = websocket.WebSocketApp(
        "ws://206.87.112.30:8000/ml-ws",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.on_open = on_open
    ws.run_forever()
    # app.run(host="0.0.0.0", port=5000)  # debug=True causes Restarting with stat
