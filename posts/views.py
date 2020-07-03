from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(reverse('index'))
    return render(request, 'new_post.html', {'form': form, 'is_edit': False})


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    slugged_group = get_object_or_404(Group, slug=slug)
    selected_posts = slugged_group.posts.all()
    paginator = Paginator(selected_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html',
                  {'page': page, 'paginator': paginator,
                   'group': slugged_group}
                  )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=user):
        following = True
    return profile_render(request, user, following)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    posts_count = post.author.posts.count()
    form = CommentForm()
    following = False
    if request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=post.author):
        following = True
    same_user = True
    if request.user != post.author:
        same_user = False
    comments = post.comments.select_related('author')
    followers_count = Follow.objects.filter(author=post.author).count()
    followings_count = Follow.objects.filter(user=post.author).count()
    return render(request, 'post.html',
                  {
                      'post': post,
                      'author': post.author,
                      'posts_count': posts_count,
                      'form': form,
                      'items': comments,
                      'following': following,
                      'same_user': same_user,
                      'followers_count': followers_count,
                      'followings_count': followings_count
                  }
                  )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect(reverse("post", kwargs=
        {
            'username': username,
            'post_id': post_id
        }
                                ))
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect(reverse('post', kwargs=
        {'username': username, 'post_id': post_id}))
    return render(request, 'new_post.html',
                  {'form': form, 'post': post, 'is_edit': True})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            form.save()
            return redirect(reverse("post", kwargs={
                'username': username, 'post_id': post_id}))
    else:
        return redirect(reverse("post", kwargs={
            'username': username, 'post_id': post_id}))


@login_required
def follow_index(request):
    post_list = Post.objects.select_related('author').filter(
        author__following__user=request.user)

    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if not Follow.objects.filter(user=request.user,
                                 author=user) and request.user != user:
        Follow.objects.create(user=request.user, author=user)
        following = True
    else:
        following = False
    return profile_render(request, user, following)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    following = False
    if Follow.objects.filter(user=request.user, author=user):
        Follow.objects.filter(user=request.user, author=user).delete()
    return profile_render(request, user, following)


def profile_render(request, user, following):
    same_user = True
    if request.user != user:
        same_user = False
    posts_list = user.posts.all()
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    posts_count = posts_list.count()
    followers_count = Follow.objects.filter(author=user).count()
    followings_count = Follow.objects.filter(user=user).count()
    return render(
        request,
        'profile.html',
        {
            'author': user,
            'page': page,
            'paginator': paginator,
            'following': following,
            'posts_count': posts_count,
            'same_user': same_user,
            'followers_count': followers_count,
            'followings_count': followings_count

        }
    )
