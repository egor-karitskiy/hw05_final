from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('pk', 'text', 'image', 'author', 'pub_date')
        model = Post
        read_only_fields = ['author']
