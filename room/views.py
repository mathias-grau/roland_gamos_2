from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from asgiref.sync import async_to_sync
import json

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from django.http import HttpResponse
from channels.layers import get_channel_layer
from django.core import serializers
from .models import Room, Message

@login_required
def rooms(request):
    rooms = Room.objects.all()

    return render(request, 'room/rooms.html', {'rooms': rooms})

@login_required
def room(request, slug):
    messages = Message.objects.filter(room=room).order_by('-timestamp')[:50]

    if request.method == 'POST':
        content = json.load(request)['content']
        author = json.load(request)['username']
        room = get_object_or_404(Room, slug=slug)
        
        
        
        
        data = {
            
        }
        return JsonResponse(data)
    
    room = get_object_or_404(Room, slug=slug)
    return render(request, 'core/chat.html', {'room': room, 'messages': reversed(messages)})
@login_required
def createroom(request):
    if request.method == "POST" :
        name = request.POST.get('roomname')
        print(name)
        user = request.user
        room = Room(name=name,
                    slug = ''.join(filter(str.isalpha, name)))
        room=room.save()
        room.members.add(user)
        room.turn_player = user
        return render(request, 'room/room.html', {'room': room, 'messages': ''})
    return render(request, 'room/createroom.html')


