from django.db import models
from django.forms import CharField, Textarea
from markdownx.fields import MarkdownxFormField


# Create your models here.
class Wiki(models.Model):
    name = models.CharField(max_length=40)
    text = models.TextField(max_length=6000)

    def __str__(self):
        return f"{self.name}: {self.text}"

class Edit(models.Model):
    text = MarkdownxFormField()

    def __str__(self):
        return f"{self.text}"