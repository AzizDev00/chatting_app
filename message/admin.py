from django.contrib import admin
from .models import Contacts, Friends, Group, Message, Reaction

admin.site.register(Group)
admin.site.register(Contacts)
admin.site.register(Message)
admin.site.register(Friends)
admin.site.register(Reaction)
