# home/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from message.models import Group 
from users.models import User

@login_required
def home_page(request):
    user = request.user
    groups = Group.objects.filter(users=user)  
    users = User.objects.exclude(id=user.id) 
    return render(request, 'index.html', {'user': user, 'groups': groups, 'users': users})
