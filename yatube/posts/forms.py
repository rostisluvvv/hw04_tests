from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Text of post'),
            'group': _('Group'),
        }
        help_texts = {
            'text': _('Enter the text of the post'),
            'group': _('Select a group'),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
