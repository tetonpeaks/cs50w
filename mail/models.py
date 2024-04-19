from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Email(models.Model): #ForeignKey, ManytoMany, CharField, etc...are types of fields in Django
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="emails") #ForeignKey references another table, CASCADE deletes references/links, related_name is arg that allows access to relationship in reverse
    sender = models.ForeignKey("User", on_delete=models.PROTECT, related_name="emails_sent")
    recipients = models.ManyToManyField("User", related_name="emails_received") #every Email has recipients which has a many-to-many relationship with User class, related_name if you have 'emails_recieved' attribute can use 'recipients' attribute access all emails or vice-versa
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.email,
            "recipients": [user.email for user in self.recipients.all()],
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "read": self.read,
            "archived": self.archived
        }
