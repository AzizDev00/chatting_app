from django.urls import path
from .views import UserMessageView, GroupChatView, GroupCreateView, AddUserToGroupView, GroupDetailView

app_name = 'message'

urlpatterns = [
    path('group/<int:pk>/', GroupChatView.as_view(), name='group_chat'),
    path('message/<int:user_id>/', UserMessageView.as_view(), name='user_message_view'),
    path('create_group/', GroupCreateView.as_view(), name='group_create'),
    path('group/<int:group_id>/add_user/', AddUserToGroupView.as_view(), name='add_user_to_group'),
    path('group/<int:pk>/detail/', GroupDetailView.as_view(), name='group_detail'),
]