user_clubs = []

from bookclub.models import Message
from django.shortcuts import render

def inbox_count(request):
    inbox_count = Message.objects.filter(receiver_user=request.user, is_read=False).count()
    request.user.inbox_count = inbox_count
    request.user.save()
    
