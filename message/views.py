from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, FormView
from .models import Message, Group, User
from .forms import MessageForm, AddUserToGroupForm, GroupCreateForm
from django.views import View
from django.db.models import Q


class UserMessageView(LoginRequiredMixin, View):
    template_name = 'message/user_message.html'
    form_class = MessageForm

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            return redirect('home:home-page')  # Redirect to home or another appropriate view

        messages = Message.objects.filter(
            Q(sender=request.user) & Q(receiver=user) |
            Q(sender=user) & Q(receiver=request.user)
        ).order_by('-timestamp')

        form = self.form_class()
        users = User.objects.exclude(id=request.user.id)
        groups = Group.objects.filter(users=request.user)

        return render(request, self.template_name, {
            'user': user,
            'messages': messages,
            'form': form,
            'users': users,
            'groups': groups,
        })

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            return redirect('home:home-page')  # Redirect to home or another appropriate view

        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = user
            message.save()
            return redirect('message:user_message_view', user_id=user.id)

        messages = Message.objects.filter(
            Q(sender=request.user) & Q(receiver=user) |
            Q(sender=user) & Q(receiver=request.user)
        ).order_by('-timestamp')

        users = User.objects.exclude(id=request.user.id)
        groups = Group.objects.filter(users=request.user)

        return render(request, self.template_name, {
            'user': user,
            'messages': messages,
            'form': form,
            'users': users,
            'groups': groups,
        })

class GroupCreateView(LoginRequiredMixin, View):
    template_name = 'message/group_create.html'
    form_class = GroupCreateForm

    def get(self, request):
        form = self.form_class()
        users = User.objects.exclude(id=request.user.id)
        groups = Group.objects.filter(users=request.user)
        return render(request, self.template_name, {
            'form': form,
            'users': users,
            'groups': groups,
        })

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            group.users.add(request.user)
            group.admins.add(request.user)
            group.save()
            return redirect('message:group_detail', pk=group.pk)

        users = User.objects.exclude(id=request.user.id)
        groups = Group.objects.filter(users=request.user)
        
        return render(request, self.template_name, {
            'form': form,
            'users': users,
            'groups': groups,
        })


class AddUserToGroupView(LoginRequiredMixin, View):
    template_name = 'message/add_user_to_group.html'
    form_class = AddUserToGroupForm

    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'group': group})

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            group.users.add(user)
            group.save()
            return redirect('message:group_detail', pk=group.pk)
        return render(request, self.template_name, {'form': form, 'group': group})

class GroupDetailView(LoginRequiredMixin, View):
    template_name = 'message/group_detail.html'

    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        return render(request, self.template_name, {'group': group})

class GroupChatView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Group
    template_name = 'message/group_chat.html'
    context_object_name = 'group'

    def test_func(self):
        group = self.get_object()
        return self.request.user in group.users.all()
    
    def handle_no_permission(self):
        return HttpResponseForbidden('You are not allowed to view this page')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.get_object().messages.all().order_by('-timestamp')
        context['form'] = MessageForm()
        context['users'] = User.objects.exclude(id=self.request.user.id)
        context['groups'] = Group.objects.filter(users=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        group = self.get_object()
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = group.users.first() 
            message.save()
            group.messages.add(message)
            group.last_message = message
            group.save()
            form = MessageForm()
        
        users = User.objects.exclude(id=request.user.id)
        groups = Group.objects.filter(users=request.user)

        context = {
            'group': group,
            'messages': group.messages.all().order_by('-timestamp'),
            'form': form,
            'users': users,
            'groups': groups,
        }
        return render(request, self.template_name, context)
