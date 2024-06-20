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
            return redirect('home:home-page') 

        messages = Message.objects.filter(
            Q(sender=request.user) & Q(receiver=user) |
            Q(sender=user) & Q(receiver=request.user)
        ).order_by('timestamp')

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
            return redirect('home:home-page') 

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
        ).order_by('timestamp')

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

    def get_context_data(self, request, **kwargs):
        context = kwargs
        # Exclude the current user from the users list
        context['users'] = User.objects.exclude(id=request.user.id)
        # Filter groups where the current user is a member
        context['groups'] = Group.objects.filter(users=request.user)
        return context

    def get(self, request, pk):
        group = get_object_or_404(Group, id=pk)

        if request.user not in group.admins.all():
            return HttpResponseForbidden('You are not allowed to add users to this group')
        
        form = self.form_class()
        context = self.get_context_data(request, form=form, group=group)
        return render(request, self.template_name, context)

    def post(self, request, pk):
        group = get_object_or_404(Group, id=pk)

        if request.user not in group.admins.all():
            return HttpResponseForbidden('You are not allowed to add users to this group')
        
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            group.users.add(user)
            group.save()
            return redirect('message:group_detail', pk=group.pk)
        
        context = self.get_context_data(request, form=form, group=group)
        return render(request, self.template_name, context)

def group_detail(request, pk):
    group = get_object_or_404(Group, id=pk)
    
    if request.user not in group.users.all():
        return HttpResponseForbidden('You are not a member of this group')
    
    users = User.objects.exclude(id=request.user.id) 
    groups = Group.objects.filter(users=request.user)
    
    context = {
        'group': group,
        'users': users,
        'groups': groups,
    }
    return render(request, 'message/group_detail.html', context)


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
