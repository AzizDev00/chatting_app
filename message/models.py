from django.db import models
from users.models import User

class Message(models.Model):
    text = models.CharField(max_length=500)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    photo = models.ImageField(upload_to='messages/photos', blank=True, null=True)
    file = models.FileField(upload_to='messages/files', blank=True, null=True)
    audio = models.FileField(upload_to='messages/audio', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    class Meta:
        db_table = 'message'
        ordering = ['-timestamp']

    def __str__(self):
        return f"To: {self.receiver} From: {self.sender} Message: {self.text}"

class Friends(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends_with')

    class Meta:
        db_table = 'friends'
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"User: {self.user} is friends with {self.friend}"

class Reaction(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=20)

    class Meta:
        unique_together = ('message', 'user', 'reaction_type')

    def __str__(self):
        return f"{self.user} reacted with {self.reaction_type} to {self.message}"

class Group(models.Model):
    name = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    users = models.ManyToManyField(User, related_name='group_memberships')
    admins = models.ManyToManyField(User, related_name='admin_groups')
    messages = models.ManyToManyField(Message, related_name='group_messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    last_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, related_name='last_message_in_group')

    class Meta:
        db_table = 'group'
        ordering = ['-timestamp']

    def __str__(self):
        return self.name

    def add_user(self, user):
        self.users.add(user)

    def add_admin(self, user):
        self.admins.add(user)
        self.add_user(user)

class Contacts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_of')

    class Meta:
        db_table = 'contacts'
        unique_together = ('user', 'contact')

    def __str__(self):
        return f"User: {self.user} has contact {self.contact}"
