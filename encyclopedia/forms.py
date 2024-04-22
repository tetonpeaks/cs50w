from django.forms import ModelForm, CharField, Textarea

from .models import Wiki, Edit

from markdownx.fields import MarkdownxFormField

class WikiForm(ModelForm):
    class Meta:
        model = Wiki
        fields = ['name','text']

    name = CharField(label="name", max_length=20)
    text = CharField(
        label="text",
        required=True,
    )

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) > 0:
            return text
        return self.errors

class EditForm(ModelForm):
    text = MarkdownxFormField()

    class Meta:
        model = Edit
        fields = ['text']

    text = CharField(label="text", widget=Textarea())