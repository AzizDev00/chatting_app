from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, FormView
from .models import Message, Group, User
from .forms import MessageForm, AddUserToGroupForm, GroupCreateForm
from django.views import View
from django.db.models import Q
from django.contrib.auth.decorators import login_required

class UserMessageView(LoginRequiredMixin, View):
    template_name = 'message/user_message.html'
    form_class = MessageForm

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            return redirect('home:home-page') 

        query = request.GET.get('q')
        messages = Message.objects.filter(
            Q(sender=request.user, receiver=user) |
            Q(sender=user, receiver=request.user)
        ).order_by('timestamp')
        if query:
            messages = messages.filter(text__icontains=query)

        form = self.form_class()
        users = User.objects.exclude(id=request.user.id)
        groups = Group.objects.filter(users=request.user)

        return render(request, self.template_name, {
            'user': user,
            'messages': messages,
            'form': form,
            'users': users,
            'groups': groups,
            'search_query': query
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

        query = request.GET.get('q')
        messages = Message.objects.filter(
            Q(sender=request.user, receiver=user) |
            Q(sender=user, receiver=request.user)
        ).order_by('timestamp')
        if query:
            messages = messages.filter(text__icontains=query)

        users = User.objects.exclude(id=request.user.id)
        groups = Group.objects.filter(users=request.user)

        return render(request, self.template_name, {
            'user': user,
            'messages': messages,
            'form': form,
            'users': users,
            'groups': groups,
            'search_query': query
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

@login_required
def group_chat(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    messages = group.message_set.all()

    query = request.GET.get('q')
    if query:
        messages = messages.filter(text__icontains=query)

    users = User.objects.all()
    groups = Group.objects.all()

    return render(request, 'message/group_chat.html', {
        'group': group,
        'messages': messages,
        'users': users,
        'groups': groups,
        'search_query': query
    })

@login_required
def user_message_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)

    query = request.GET.get('q')
    if query:
        messages = messages.filter(text__icontains=query)

    users = User.objects.all()
    groups = Group.objects.all()

    return render(request, 'message/user_message.html', {
        'user': user,
        'messages': messages,
        'users': users,
        'groups': groups,
        'search_query': query
    })


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
        group = self.get_object()
        query = self.request.GET.get('q')
        messages = group.messages.all().order_by('-timestamp')
        if query:
            messages = messages.filter(text__icontains=query)

        context.update({
            'messages': messages,
            'form': MessageForm(),
            'users': User.objects.exclude(id=self.request.user.id),
            'groups': Group.objects.filter(users=self.request.user),
            'search_query': query,
        })
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

        query = request.GET.get('q')
        messages = group.messages.all().order_by('-timestamp')
        if query:
            messages = messages.filter(text__icontains=query)

        context = {
            'group': group,
            'messages': messages,
            'form': form,
            'users': User.objects.exclude(id=request.user.id),
            'groups': Group.objects.filter(users=request.user),
            'search_query': query
        }
        return render(request, self.template_name, context)

class EditMessageView(LoginRequiredMixin, View):
    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id, sender=request.user)
        text = request.POST.get('text')
        if text:
            message.text = text
            message.save()
            return JsonResponse({'success': True, 'new_text': message.text})
        return JsonResponse({'success': False})


class DeleteMessageView(LoginRequiredMixin, View):
    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id, sender=request.user)
        message.delete()
        return JsonResponse({'success': True})


class SearchView(LoginRequiredMixin, View):
    template_name = 'message/search_results.html'

    def get(self, request):
        query = request.GET.get('q', '')
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
        groups = Group.objects.filter(name__icontains=query, users=request.user)

        context = {
            'query': query,
            'users': users,
            'groups': groups,
        }
        return render(request, self.template_name, context)
