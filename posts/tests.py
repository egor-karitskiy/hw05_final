from django.core.cache import cache
from django.core.files import File
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.test import Client

from .models import Post, Group
from django.urls import reverse

User = get_user_model()


@override_settings(CACHES={'default':
    {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
class Sprint6Tests(TestCase):
    def setUp(self):
        self.not_logged_in_client = Client()
        self.client = Client()
        self.new_group = Group.objects.create(title='Pigs', slug='pigs')
        self.another_group = Group.objects.create(title='Wolves',
                                                  slug='wolves')
        self.post_text = 'We are not afraid of Gray Wolf!'
        self.one_more_text = 'Where are you stupid gray wolf?!'
        self.test_user = User.objects.create_user(username='nifnif')
        self.client.force_login(self.test_user)
        self.image = open('media/mk.jpg', 'rb')
        self.image_file = File(self.image)

    def test_new_user_profile_exists(self):
        response = self.client.get(
            reverse('profile', kwargs={'username': self.test_user.username})
        )
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_create_new_post(self):
        self.client.post(reverse('new_post'),
                         data={'group': self.new_group.id,
                               'text': self.post_text
                               },
                         follow=True)
        urls_list = [reverse('index'),
                     reverse('profile',
                             kwargs={'username': self.test_user.username}),
                     reverse('post',
                             kwargs={'username': self.test_user.username,
                                     'post_id': 1}),
                     reverse('group_slug',
                             kwargs={'slug': self.new_group.slug})]
        for url in urls_list:
            self.check_in_response(url,
                                   self.post_text,
                                   self.new_group.title,
                                   self.test_user.username)
        self.assertEqual(Post.objects.count(), 1)

    def test_non_authenticated_user_redirected_to_login_page(self):
        response = self.not_logged_in_client.post(
            reverse('new_post'),
            data={'text': self.post_text, 'group': self.new_group},
            follow=True)
        expected_url = reverse('login') + "?next=" + reverse('new_post')
        self.assertRedirects(response, expected_url)
        self.assertEqual(Post.objects.count(), 0)

    def check_in_response(self, url, text, group, username):
        self.client.get(url)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, text)
        self.assertContains(resp, group)
        self.assertContains(resp, username)

    def test_new_post_appears_on_proper_pages(self):
        Post.objects.create(author=self.test_user,
                            text=self.post_text,
                            group=self.new_group
                            )
        urls_list = [reverse('index'),
                     reverse('profile',
                             kwargs={'username': self.test_user.username}),
                     reverse('post',
                             kwargs={'username': self.test_user.username,
                                     'post_id': 1}),
                     reverse('group_slug',
                             kwargs={'slug': self.new_group.slug})]

        for url in urls_list:
            self.check_in_response(url,
                                   self.post_text,
                                   self.new_group.title,
                                   self.test_user.username)

    def test_authenticated_user_can_edit_own_posts(self):
        one_more_test_post = Post.objects.create(author=self.test_user,
                                                 text=self.post_text,
                                                 group=self.new_group
                                                 )
        self.client.post(reverse('post_edit',
                                 kwargs={'username': self.test_user.username,
                                         'post_id': one_more_test_post.id}),
                         data={'text': self.one_more_text,
                               'group': self.another_group.id},
                         follow=True)
        urls_list = [
            reverse('index'),
            reverse('profile',
                    kwargs={
                        'username': self.test_user.username}),
            reverse('post',
                    kwargs={'username': self.test_user.username,
                            'post_id': one_more_test_post.id}),
            reverse('group_slug',
                    kwargs={'slug': self.another_group.slug})
        ]

        for url in urls_list:
            self.check_in_response(url,
                                   self.one_more_text,
                                   self.another_group.title,
                                   self.test_user.username)

    def test_404_status_code_works(self):
        response = self.client.get(
            '/wrong_url_never_appeared/')
        self.assertEqual(response.status_code, 404)

    def test_image_tags_appear_on_proper_pages(self):
        post_with_image = Post.objects.create(author=self.test_user,
                                              text=self.post_text,
                                              group=self.new_group,
                                              image=self.image_file
                                              )
        urls_list = [reverse('index'),
                     reverse('profile',
                             kwargs={'username': self.test_user.username}),
                     reverse('post',
                             kwargs={'username': self.test_user.username,
                                     'post_id': post_with_image.id}),
                     reverse('group_slug',
                             kwargs={'slug': self.new_group.slug})]

        for url in urls_list:
            self.check_in_response(url,
                                   self.post_text,
                                   self.new_group.title,
                                   self.test_user.username)

            self.assertContains(self.client.get(url), '<img')

    def test_non_image_file_form_response(self):
        post_with_image = Post.objects.create(author=self.test_user,
                                              text=self.post_text,
                                              group=self.new_group,
                                              image=self.image_file
                                              )
        self.non_image = open('media/pigs.txt', 'rb')
        self.non_image_file = File(self.non_image)
        response = self.client.post(
            reverse('post_edit',
                    args=[self.test_user.username, post_with_image.id]),
            data={'text': self.one_more_text, 'image': self.non_image_file},
            follow=True
        )

        error_description = 'Upload a valid image. The file you ' \
                            'uploaded was either not an image ' \
                            'or a corrupted image.'
        self.assertFormError(response, 'form', 'image', error_description)


class Sprint6TestsCachedTests(TestCase):
    def setUp(self):
        self.not_logged_in_client = Client()
        self.client = Client()
        self.new_group = Group.objects.create(title='Pigs', slug='pigs')
        self.another_group = Group.objects.create(title='Wolves',
                                                  slug='wolves')
        self.post_text = 'We are not afraid of Gray Wolf!'
        self.one_more_text = 'Where are you stupid gray wolf?!'
        self.test_user = User.objects.create_user(username='nifnif')
        self.client.force_login(self.test_user)
        self.image = open('media/mk.jpg', 'rb')
        self.image_file = File(self.image)

    def test_cache_index_page(self):
        cache.clear()
        Post.objects.create(
            text=self.post_text, author=self.test_user, group=self.new_group)
        response1 = self.client.get(reverse('index'))
        Post.objects.create(
            text=self.one_more_text,
            author=self.test_user,
            group=self.another_group)
        response2 = self.client.get(reverse('index'))
        self.assertEqual(response1.content,
                         response2.content)
        cache.clear()
        response3 = self.client.get(reverse('index'))
        self.assertNotEqual(response1.content,
                            response3.content)
