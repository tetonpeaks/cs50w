from django.forms import ModelForm, Form, ChoiceField, CharField, DecimalField, URLField, ValidationError
from auctions.models import Listing, Bid, Comment

class ListingForm(ModelForm):
    class Meta:
            model = Listing
            fields = ['title', 'description', 'image_url', 'category', 'current_price']

    def current_price(self):
        current_price = float(self.cleaned_data.get('current_price'))
        if isinstance(current_price, float) and current_price > 0: return current_price
        raise ValidationError('The current price needs to be greater than 0.')

    def clean_category(self):
        category = self.cleaned_data.get('category')
        return category.lower()

class CommentForm(ModelForm):
    class Meta:
            model = Comment
            fields = ['user', 'text', 'listing']

    text = CharField(label='', required=True)

    def clean_comment(self):
        text = self.cleaned_data.get('text')
        if len(text) > 0: return text
        return self.errors