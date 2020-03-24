import os
from matplotlib import pyplot as plt
import cv2

def clahe_rgb(img, clip_lim = 2.0, tile_size = (8,8)):
    clahe = cv2.createCLAHE(clipLimit = clip_lim, tileGridSize = tile_size)
    new_img = img.copy()
    new_img[:,:,0] = clahe.apply(img[:,:,0])
    new_img[:,:,1] = clahe.apply(img[:,:,1])
    new_img[:,:,2] = clahe.apply(img[:,:,2])
    return new_img

def equalize_hist_rgb(img):
    equ = img.copy()
    equ[:,:,0] = cv2.equalizeHist(img[:,:,0])
    equ[:,:,1] = cv2.equalizeHist(img[:,:,1])
    equ[:,:,2] = cv2.equalizeHist(img[:,:,2])
    return equ

def show_img_hist(img):
    fig, ax = plt.subplots(1, 2, figsize = (10,5))
    ax[0].imshow(img)
    histr = cv2.calcHist([img],[0],None,[256],[0,256])  
    ax[1].plot(histr) 
    return