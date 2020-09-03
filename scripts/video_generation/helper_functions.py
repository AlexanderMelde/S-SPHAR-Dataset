import os
import numpy as np

def hex2rgb(hex_string, fix_unity):
    # Example: Input: #B4FBB8 Output: (180, 251, 184)
    # `fix_unity` will fix one-pixel-off errors from unity engine
    # https://stackoverflow.com/a/29643643/
    hex_string = hex_string.lstrip('#')
    hex_string = hex_string.replace("80","7f") if fix_unity else hex_string
    return tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))

def rgb2bgr(rgb):
    return rgb[::-1] # reverse list out of place

def get_equal_white_pixel_count(img1, img2):
    return np.count_nonzero(np.bitwise_and(img1 == img2,img1))

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '\033[93m'+'%s:%s: %s: %s\n' % (os.path.basename(filename), lineno, category.__name__, message)+'\033[0m'
 
