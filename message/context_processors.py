from .models import Group, User

def sidebar_data(request):
    users = User.objects.all()
    groups = Group.objects.all()
    return {
        'users': users,
        'groups': groups
    }
