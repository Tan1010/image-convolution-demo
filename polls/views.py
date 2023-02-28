from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import urllib.request
from PIL import Image
import numpy as np
import cv2
import os
from django.conf import settings
from django.templatetags.static import static
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def index(request):
    return render(request, 'polls/index.html')

def convolve(request):
    if request.method == 'POST':
        image_url=request.POST['image']
        width = request.POST['image_width']
        height = request.POST['image_height']
        pixel_value = request.POST['pixel_value']
        kernel_value = request.POST.getlist('kernel[]')
        

        with urllib.request.urlopen(image_url) as url:
            img = Image.open(url, 'r').convert('L')
        
        pixel = np.array(img.getdata())
        pixel.resize(img.size[1],img.size[0])
        kernel = np.array([[float(kernel_value[0]),float(kernel_value[1]),float(kernel_value[2])], [float(kernel_value[3]),float(kernel_value[4]),float(kernel_value[5])], [float(kernel_value[6]),float(kernel_value[7]),float(kernel_value[8])]])

        new_img = conv(pixel, kernel)

        context = {
            'kernel' : kernel_value,
        }
      
        cv2.imwrite(os.path.join(settings.STATICFILES_DIRS[0], 'polls/cv2_new_img.png'), new_img)

        return render(request, 'polls/image_convolution.html', context)

def conv(image, kernel):
    new_image = np.zeros([len(image)-2, len(image[0])-2])
    kernel = np.flipud(np.fliplr(kernel))
    for row in range(image.shape[0]):
        first_row_index = row
        last_row_index = row+3
        if last_row_index <= image.shape[0]:
            for column in range(image.shape[1]):
                first_column_index = column
                last_column_index = column+3
                if last_column_index <= image.shape[1]:
                    temp_array = image[first_row_index:last_row_index,first_column_index:last_column_index]
                    new_image[row][column] = round(np.sum(np.multiply(kernel, temp_array)))

    return new_image


