class SearchResultsView(UserListView):
    model = user
    template_name = 'user_list.html'
    def get_queryset(self):
        return user.objects.filter(
        Q(name__icontains='John') | Q(name__icontains='Doe')
)
