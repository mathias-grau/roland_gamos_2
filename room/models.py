from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    turn_player = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    # members of the group
    members = models.ManyToManyField(User,related_name = 'member')

class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)