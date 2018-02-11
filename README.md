# 微信跳一跳辅助工具
## 准备：
    1. python3.6.2
    2. 一部Android手机或模拟器
    3. adb驱动
    4. OpenCV-python==3.4.0和numpy==1.13.1
##  基本思路：
* 获取棋子的中心位置chess_center()
* 获取下一个方块的中心位置white_center()或get_center()
* 通过函数关系获得按压时间jump()，以及通过os模块和adb命令获取截屏update_screen()

### 1. 获取棋子的中心位置
使用OpenCV中模板匹配实现
提供棋子图片chess.png
<div align=center><img src="https://github.com/m564859663/WeChat_Jump/blob/master/chess.png"/></div>

```python
from cv2 import *
import numpy as np

def chess_center(img_screen, img_temp):
    res = matchTemplate(img_screen, img_temp, TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = minMaxLoc(res)
    temp_center = (max_loc[0] + 47, max_loc[1] + 188)
    return temp_center

img_chess = imread('chess.png', 0)
img_auto = update_screen()#更新屏幕函数
first_center = chess_center(img_auto, img_chess)#棋子中心
```

通过以下程序验证匹配效果
```python
from cv2 import *

img_chess = imread('chess.png')
img_auto = imread('autojump.png')
res = matchTemplate(img_auto, img_chess, TM_CCOEFF)
min_val, max_val, min_loc, max_loc = minMaxLoc(res)
top_left = max_loc
bottom_right = (top_left[0]+img_chess.shape[1], top_left[1]+img_chess.shape[0])
img = cv2.rectangle(img_auto, top_left, bottom_right, (0, 0, 255), 3)
imwrite("verify.png", img)
```
<div align=center><img height=360 width=540 src="https://github.com/m564859663/WeChat_Jump/blob/master/verify.png"/></div>

> 参考自
> [模板匹配](http://blog.csdn.net/firemicrocosm/article/details/48374979)
> [几何图形绘制](http://blog.csdn.net/guduruyu/article/details/68490206)

### 2. 获取下一个方块的中心位置
①当方块有白点时：
采用与上一节中相同的模板匹配方法，提供模板white.png
<div align=center><img src="https://github.com/m564859663/WeChat_Jump/blob/master/white.png"/></div>

②当方块为白色或方块未出现白点时，即匹配率低于95%时采用canny边缘算法
```python
def get_center(img, fst_center):
    # 利用canny边缘检测的结果寻找物块的上沿和下沿
    # 计算物块的中心点
    img = GaussianBlur(img, (7, 7), 0)  # 高斯模糊
    canny_img = cv2.Canny(img, 1, 10)
    h, w = canny_img.shape
    # 将棋子抹除，以防出现棋子高于下一个方块的情况
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
```
### 3. 通过函数关系获得按压时间，并用os模块和adb命令执行

```
def jump(cen1, cen2):
    length = (cen1[0] - cen2[0]) ** 2 + (cen1[1] - cen2[1]) ** 2
    press_time = int(length ** 0.5 * 1.36)
    rand = random.randint(0, 9) * 10
    cmd = ('adb shell input swipe %i %i %i %i ' + str(press_time)) \
            % (320 + rand, 410 + rand, 320 + rand, 410 + rand)
    os.system(cmd)
    print(cmd)
```

> 参考
> [用Python+Opencv让电脑帮你玩微信跳一跳](https://zhuanlan.zhihu.com/p/32502071)
