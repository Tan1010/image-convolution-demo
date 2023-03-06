from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('convolve', views.convolve, name='convolve'),
    path('<slug:slug>', views.deleteImage, name='deleteImage'),
]
