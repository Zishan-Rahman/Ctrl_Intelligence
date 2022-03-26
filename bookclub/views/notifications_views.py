from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from bookclub.models import *
from django.views.generic.edit import View


class CommentNoticeListView(LoginRequiredMixin, ListView):
    context_object_name = 'notices'
    template_name = 'notif_list.html'
    def get_queryset(self):
        return self.request.user.notifications.unread()

class CommentNoticeUpdateView(View):
    def get(self, request):
        notice_id = request.GET.get('notice_id')
        if notice_id:
            message = Message.objects.get(id=request.GET.get('message_id'))
            request.user.notifications.get(id=notice_id).mark_as_read()
            return redirect('home')
        else:
            request.user.notifications.mark_all_as_read()
            return redirect('notice:list')