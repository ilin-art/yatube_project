from django import forms
from .models import Post, Group, Comment


class PostForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects,
        empty_label='---------',
        required=False,
        label='Группа'
    )

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
