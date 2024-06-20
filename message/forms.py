from django import forms
from .models import Message, Group, User

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'photo', 'file', 'audio']

class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class AddUserToGroupForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")
