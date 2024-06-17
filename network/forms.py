from django.forms import ModelForm, CharField, Textarea
from network.models import Posts

class PostForm(ModelForm):
    class Meta:
            model = Posts
            fields = ['text']

    #text = CharField(
    #    label='',
    #    required=True,
    #)

    text = CharField(label="", widget=Textarea())

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) > 0:
            return text
        return self.errors