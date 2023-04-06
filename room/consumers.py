import json

from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Room, Message
import requests

# Set the base URL for the MusicBrainz API
base_url = "http://musicbrainz.org/ws/2/"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']  # change room_name to room_id
        self.room_group_name = 'chat_%s' % self.room_id

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, code=None):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print("receive function()")
        data = json.loads(text_data)
        print('data', data)
        message = data['message']
        username = data['username']
        room = data['room']
        current_artist = data['current_artist']
        previous_artist = data['previous_artist']
        title = data['title']
        print("The current artist return by data is ",current_artist)
        print("The previous artist return by data is ",previous_artist)
        print('The title return by data is',title)
        
        test = await self.test_artist(message,current_artist)
        
        if test['status'] == 1:
            await self.save_message(username, room, message)
            previous_artist = current_artist
            current_artist = message
            title = test['title']
            await self.update_current_artist_and_title(room, current_artist,previous_artist,title)
            

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'current_artist': current_artist,
                'previous_artist': previous_artist,
                'title': title,
            }
        
        )
        print("The current artist is",current_artist)
        print("The previous artist is",previous_artist)
        print("The title of the featuring is",title)

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        current_artist = event['current_artist']
        previous_artist = event['previous_artist']
        title=event['title']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'current_artist' : current_artist,
            'previous_artist' : previous_artist,
            'title': title,
        }))

    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room)
        Message.objects.create(user=user, room=room, content=message)
        
    @sync_to_async
    def update_current_artist_and_title(self, room, current_artist,previous_artist,title):
        print("update_current_artist_and_title function()")
        room = Room.objects.get(slug=room)
        room.current_artist = current_artist
        room.previous_artist = previous_artist
        room.title=title
        print("New current artist",room.current_artist)
        print("New title",room.title)
        room.save()
        
    @sync_to_async
    def test_artist(self,message,current_artist):
        print("test_artist function()")
        artist_1=message
        artist_2=current_artist
        
        context = {}
    
    
        # Set the parameters for the API request
        params = {
        "query":  f"artist:{artist_1} AND artist:{artist_2}",
        "fmt": "json",
        }

        # Make the API request
        response = requests.get(base_url + "recording", params=params)
    
        if response.status_code == 200:
            # If the request was successful, parse the JSON response
            data = response.json()
            
            
            if len(data["recordings"]) > 0:
                title = data["recordings"][0]['title']
                # If there were releases returned, that means the two artists have collaborated
                context['current_artist']=  artist_1
                context['title']= title
                context['status']= 1
                return context
                
            else:
                context['current_artist']=  artist_1
                context['status']= 2
                return context
        else:
            context['current_artist']=  artist_1
            context['status']= 3
            #connection issue
            return context
        