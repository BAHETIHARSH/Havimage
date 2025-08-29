from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('', views.image_list, name='image_list'),
    path('images/<int:pk>/', views.image_detail, name='image_detail'),  
    path('images/<int:pk>/edit/', views.edit_image, name='edit_image'),
    path('images/<int:pk>/delete/', views.delete_image, name='delete_image'),
    path('download/<int:pk>/', views.download_image, name='download_image'),

]
