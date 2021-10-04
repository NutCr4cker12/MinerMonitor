import cv2
from PIL import ImageGrab
import numpy as np

def get_image_position(img_name, thershold = 0.8, bbox = None, return_corner: bool = False):
    """ Returns image center position (x, y) in screen. Returns (None, None) if not found """
    screen = ImageGrab.grab(bbox=bbox)
    img_rgb = np.array(screen)

    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

    template = cv2.imread(img_name, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= thershold)
    for pt in zip(*loc[::-1]):
        # Return the corner
        if return_corner:
            return (pt[0], pt[1])
        
        # Return the center
        return (pt[0] + w / 2, pt[1] + h / 2)
        # cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

    return (None, None)


def get_screen_shot(bbox: tuple = None):
    screen = ImageGrab.grab(bbox=bbox)
    return screen

if __name__ == "__main__":
    # get_image_position("run.PNG")
    screen = ImageGrab.grab()
    # screen.show()

    x, y = get_image_position("shared_unchecked.PNG", return_corner=True)
    print(x, y)

    if x is not None and y is not None:
        # Corner is found
        x2, y2 = get_image_position("Checked.PNG", thershold=0.8, bbox=(x, y, x + 25, y + 20))
        print("FOUND CHECKED: ", x2, y2)

        x2, y2 = get_image_position("Unchecked.PNG", thershold=0.8, bbox=(x, y, x + 25, y + 20))
        print("FOUND UNCHECKED: ", x2, y2)
    else:
        print("SHARED UNCHECKED NOT FOUND !!!")

    # bbox = (x, y, x + 25, y + 20)
    # screeen = ImageGrab.grab(bbox=bbox)
    # # screeen.show()

    # img_rgb = cv2.cvtColor(np.array(screeen), cv2.COLOR_RGB2BGR)

    # template = cv2.imread("Checked.PNG", 0)
    
    # print(img_rgb.shape)
    # print("Template shape: ", template.shape)

    # bbox = (x, y, x + 100, y + 20) # Just for test validation
    # screeen = ImageGrab.grab(bbox=bbox)
    # screeen.show()
    
