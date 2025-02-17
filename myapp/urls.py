from django.urls import path
from . import views
urlpatterns = [
    
    path('',views.index,name = 'index'),
    path('register',views.register,name = 'register'),
    path('login',views.login,name = 'login'),
    path('logout',views.logout,name ='logout'),
    path('video_capture',views.video_capture,name = 'video_capture'),
    path('video_feed',views.video_feed,name = 'video_feed'),
    path('upload_image',views.upload_image,name = 'upload_image'),
    
]