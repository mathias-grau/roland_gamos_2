from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from asgiref.sync import async_to_sync
import json

from django.shortcuts import get_object_or_404,redirect
from django.http import JsonResponse
from django.contrib.auth.models import User

from django.http import HttpResponse
from channels.layers import get_channel_layer
from django.core import serializers
from .models import Room, Message


@login_required
def rooms(request):
    rooms = Room.objects.all()

    return render(request, 'room/rooms.html', {'rooms': rooms})

@login_required
def room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    print('room', room)
    messages = Message.objects.filter(room=room).order_by('date_added').reverse()[:5][::-1]
    username = request.user.username


    return render(request, 'room/room.html', {'room': room,
                                              'messages': messages,
                                              'username': username,
                                              })
@login_required
def createroom(request):
    if request.method == "POST" :
        name = request.POST.get('roomname')
        print("trying to create room",name)
        slug = ''.join(filter(str.isalpha, name))
        current_artist = "Angèle"
        if test_room_exists(request)== False:
            
            room = Room.objects.create(name=name, 
                                       slug=slug,
                                       current_artist = current_artist,
    
                                       )
            print("room created",room)
            return redirect("room",room.id)
        
        else : 
            errors= test_room_exists(request)
            print(errors)
            return render(request, 'room/createroom.html',{'errors': errors})
    return render(request, 'room/createroom.html',{})


def test_room_exists(request):
    name = request.POST.get('roomname',None)
    if name == None:
        return "Name is none"
    slug = ''.join(filter(str.isalpha, name))
    if Room.objects.filter(slug=slug).exists():
        return "Room already exists"
    return False 

@login_required
def deleteroom(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == "POST":
        room.delete()
        return redirect('rooms')
    return render(request, 'room/deleteroom.html', {'room': room})
