from django.forms import ModelForm, Textarea

from .models import Post, Comment


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        help_texts = {
            'text': 'Пишите ваши грандиозные мысли здесь!',
            'group': 'Выберите группу для публикации :)'
            }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': Textarea(attrs={'cols': 70, 'rows':6}),
        }
