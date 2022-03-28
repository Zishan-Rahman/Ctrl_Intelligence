from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from bookclub.templates import *
from bookclub.forms import *
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from bookclub.models import *
from django.views.generic.edit import View
from django.db.models import Q


# Adapted from https://legionscript.medium.com/building-a-social-media-app-with-django-and-python-part-14-direct-messages-pt-1-1a6b8bd9fc40
class CreateChatView(View):
    """View to create a new chat between users"""
    def get(self, request, *args, **kwargs):
        """Handle get attempt"""
        form = ChatForm()
        context = {
            'form': form
        }
        return render(request, 'create_chat.html', context)

    def post(self, request, *args, **kwargs):
        """Handle post attempt"""
        form = ChatForm(request.POST)
        email = request.POST.get('email')
        try:
            receiver = User.objects.get(email=email)
            if receiver.id == request.user.id:
                #If chat is to itself
                messages.add_message(request, messages.ERROR, "You cannot create a chat with yourself!")
                return redirect('create_chat')
            if Chat.objects.filter(user=request.user, receiver=receiver).exists():
                #If chat exists and same user started it
                chat = Chat.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('chat', pk=chat.pk)

            elif Chat.objects.filter(user=receiver, receiver=request.user).exists():
                #If chat exists and different user started it
                chat = Chat.objects.filter(user=receiver, receiver=request.user)[0]
                return redirect('chat', pk=chat.pk)

            if form.is_valid():
                sender_chat = Chat(
                    user=request.user,
                    receiver=receiver
                )
                sender_chat.save()
                messages.add_message(request, messages.SUCCESS, "Chat created!")
                chat_pk = sender_chat.pk
                return redirect('chat', pk=chat_pk)
        except:
            return redirect('create_chat')


def createChatFromProfile(request, user_id):
    """View to create a chat from the user's profile"""
    try:
        receiver = User.objects.get(id=user_id)
        if Chat.objects.filter(user=request.user, receiver=receiver).exists():
            chat = Chat.objects.filter(user=request.user, receiver=receiver)[0]
            return redirect('chat', pk=chat.pk)

        sender_chat = Chat.objects.create(
            user=request.user,
            receiver=receiver
        )
        messages.add_message(request, messages.SUCCESS, "Chat created!")
        chat_pk = sender_chat.pk
        return redirect('chat', pk=chat_pk)
    except:
        return redirect('create_chat')


# Adapted from https://legionscript.medium.com/building-a-social-media-app-with-django-and-python-part-14-direct-messages-pt-1-1a6b8bd9fc40
class ListChatsView(View):
    """View to list all chats"""

    def get(self, request, *args, **kwargs):
        chats = Chat.objects.filter(Q(user=request.user) | Q(receiver=request.user))
        context = {
            'chats': chats
        }
        return render(request, 'inbox.html', context)


# Adapted from https://legionscript.medium.com/building-a-social-media-app-with-django-and-python-part-14-direct-messages-pt-1-1a6b8bd9fc40
class CreateMessageView(View):
    """View to create a new message in an already existing chat"""

    def post(self, request, pk, *args, **kwargs):
        chat = Chat.objects.get(pk=pk)
        if chat.receiver == request.user:
            receiver = chat.user
        else:
            receiver = chat.receiver
        message = Message(
            chat=chat,
            sender_user=request.user,
            receiver_user=receiver,
            body=request.POST.get('message'),
        )
        message.save()
        return redirect('chat', pk=pk)


# Adapted from https://legionscript.medium.com/building-a-social-media-app-with-django-and-python-part-14-direct-messages-pt-1-1a6b8bd9fc40
class ChatView(View):
    """View to display a user's open chat"""
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        chat = Chat.objects.get(pk=pk)
        if request.user == chat.receiver or request.user == chat.user:

            message_list = Message.objects.filter(chat__pk__contains=pk)
            context = {
                'chat': chat,
                'form': form,
                'message_list': message_list
            }
            return render(request, 'chat.html', context)

        else:
            messages.add_message(request, messages.ERROR, "Action prohibited")
            return redirect('home')
