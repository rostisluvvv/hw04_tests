from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': _('Text of post'),
            'group': _('Group'),
        }
        help_texts = {
            'text': _('Enter the text of the post'),
            'group': _('Select a group'),
        }
