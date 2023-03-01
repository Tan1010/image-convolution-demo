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
from boto3 import session
from botocore.client import Config

ACCESS_ID = 'DO004YBZTTUTRFZJ7AHT'
SECRET_KEY = '+nkHTuk9tirXP2gZo7jmgLhTQNx6348vwCkYOrTLYjE'

session = session.Session()
client = session.client('s3',
                        region_name='sgp1',
                        endpoint_url='https://image-convolution-demo.sgp1.digitaloceanspaces.com',
                        aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY)


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
      
        image_string = cv2.imencode('.jpg', new_img)[1].tostring()
        client.put_object(Bucket='images',Key='cv2_new_img.jpg',Body=image_string,ACL='public-read',ContentType='image/jpg')     
        
#         cv2.imwrite(os.path.join(settings.BASE_DIR, 'cv2_new_img.png'), new_img)
#         with open(os.path.join(settings.BASE_DIR, 'cv2_new_img.jpg'), 'rb') as file_contents:
#             client.put_object(Bucket='images',Key='new_cv2_new_img.jpg',Body=file_contents,ACL='public-read',ContentType='image/jpg')        

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


