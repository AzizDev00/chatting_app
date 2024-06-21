from django.urls import path
from .views import (
    UserMessageView, GroupCreateView, AddUserToGroupView,
    group_detail, GroupChatView, EditMessageView, DeleteMessageView, SearchView,
    group_chat, user_message_view,
)
app_name = 'message'

urlpatterns = [
    path('group/<int:pk>/', GroupChatView.as_view(), name='group_chat'),
    path('message/<int:user_id>/', UserMessageView.as_view(), name='user_message_view'),
    path('create_group/', GroupCreateView.as_view(), name='group_create'),
    path('group/<int:pk>/add_user/', AddUserToGroupView.as_view(), name='add_user_to_group'),
    path('group/<int:pk>/detail/', group_detail, name='group_detail'),
    path('message/edit/<int:message_id>/', EditMessageView.as_view(), name='edit_message'),
    path('message/delete/<int:message_id>/', DeleteMessageView.as_view(), name='delete_message'),
    path('search/', SearchView.as_view(), name='search'),
    path('group/<int:group_id>/', group_chat, name='group_chat'),
    path('user/<int:user_id>/', user_message_view, name='user_message_view'),

]
