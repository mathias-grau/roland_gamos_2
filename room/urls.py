from django.urls import path

from . import views


urlpatterns = [
    path('', views.rooms, name='rooms'),
    path('<int:room_id>', views.room, name='room'),
    path('createroom',views.createroom,name='createroom'),
    path('deleteroom/<int:room_id>',views.deleteroom,name='deleteroom')
    ]