# -*- coding: utf-8 -*-
import os, random, time
from cv2 import *
import numpy as np


def jump(cen1, cen2):
    length = (cen1[0] - cen2[0]) ** 2 + (cen1[1] - cen2[1]) ** 2
    press_time = int(length ** 0.5 * 1.36)
    rand = random.randint(0, 9) * 10
    cmd = ('adb shell input swipe %i %i %i %i ' + str(press_time)) \
            % (320 + rand, 410 + rand, 320 + rand, 410 + rand)
    os.system(cmd)
    print(cmd)


def update_screen():
    os.system('adb shell screencap -p /sdcard/autojump.png')
    os.system('adb pull /sdcard/autojump.png')
    return np.array(imread('autojump.png', 0))


def chess_center(img_screen, img_temp):
    res = matchTemplate(img_screen, img_temp, TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = minMaxLoc(res)
    temp_center = (max_loc[0] + 47, max_loc[1] + 188)
    return temp_center


def white_center(img_screen, img_temp, w, h):
    res = matchTemplate(img_screen, img_temp, TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = minMaxLoc(res)
    temp_center = (max_loc[0] + w/2, max_loc[1] + h/2)
    return [temp_center, max_val]


def get_center(img, fst_center):
    # 利用边缘检测的结果寻找物块的上沿和下沿
    # 进而计算物块的中心点
    img = GaussianBlur(img, (7, 7), 0)
    canny_img = cv2.Canny(img, 1, 10)
    h, w = canny_img.shape
    for k in range(fst_center[1] - 188, fst_center[1] + 25):
        for b in range(fst_center[0] - 57, fst_center[0] + 57):
            canny_img[k][b] = 0

    y_top = np.nonzero(canny_img[400:])[0][0]+400
    x_top = int(np.mean(np.nonzero(canny_img[y_top])))
    y_bottom = y_top + 50
    for row in range(y_bottom, h):
        if canny_img[row, x_top] != 0:
            y_bottom = row
            break

    temp_center = (x_top, (y_top + y_bottom) // 2)
    return temp_center


def main():
    # 初始化
    img_chess = imread('chess.png', 0)
    img_white = imread('white.png', 0)
    w_w, h_w = img_white.shape[::-1]
    while True:
        img_auto = update_screen()
        first_center = chess_center(img_auto, img_chess)#棋子中心
        temp = white_center(img_auto, img_white, w_w, h_w)#首先匹配白点
        if temp[1] > 0.95:
            second_center = temp[0]
            print('found white circle!')
        else:
            second_center = get_center(img_auto, first_center)
        jump(first_center, second_center)
        time.sleep(1 + random.random())


if __name__ == '__main__':
    main()
