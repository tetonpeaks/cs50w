from django.forms import Form, ModelForm, CharField, Textarea

class WikiForm(Form):
    name = CharField(label="name", max_length=20)
    text = CharField(label="text", widget=Textarea(attrs={'cols': 1, 'rows': 10}))


class EditForm(Form):
    text = CharField(label="text", widget=Textarea())