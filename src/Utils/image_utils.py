import cv2
from PIL import ImageGrab
import numpy as np

def get_image_position(img_name, thershold = 0.8):
    """ Returns image center position (x, y) in screen. Returns (None, None) if not found """
    screen = get_screen_shot()
    img_rgb = np.array(screen)
    img_gray = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2GRAY)

    # img_rgb = cv2.imread(screen)
    # img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(img_name, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= thershold)
    for pt in zip(*loc[::-1]):
        return (pt[0] + w / 2, pt[1] + h / 2)
        # cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

    # cv2.imwrite("res.png", img_rgb)
    return (None, None)


def get_screen_shot():
    screen = ImageGrab.grab()
    return screen

if __name__ == "__main__":
    get_image_position("run.PNG")