from bookclub.views import config

def menu(request):
    config.inbox_count(request)