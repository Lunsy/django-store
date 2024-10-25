from datetime import timedelta
from http import HTTPStatus

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from users.models import EmailVerification, User


class UserRegistrationViewTestCase(TestCase):

    def setUp(self):
        self.data = {
            'first_name': 'Unkindno1', 'last_name': 'Test',
            'username': 'Unkindno1', 'email': 'jobartjobs@yandex.ru',
            'password1': '12345678Aa', 'password2': '12345678Aa',
        }
        self.path = reverse('users:registration')

        # Delete a user with the same name or email
        User.objects.filter(username='Lunsy').delete()

        # Creating a fake object SocialApp
        site = Site.objects.get_current()
        social_app = SocialApp.objects.create(
            provider='github',
            name='GitHub',
            client_id='fake_client_id',
            secret='fake_secret'
        )
        social_app.sites.add(site)

    def test_user_registration_get(self):
        response = self.client.get(self.path)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(response.context_data['title'], 'Store - Регистрация')
        self.assertTemplateUsed(response, 'users/registration.html')

    def test_user_registration_post_success(self):
        username = self.data['username']
        self.assertFalse(User.objects.filter(username=username).exists())
        response = self.client.post(self.path, self.data)

        # Output response content and form errors for debugging
        # if response.status_code != HTTPStatus.FOUND:
        #     print(response.content)
        #     if 'form' in response.context:
        #         print(response.context['form'].errors)

        # check verifying user creation
        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username=username).exists())

        # check creating of email verification
        email_verification = EmailVerification.objects.filter(user__username=username)
        self.assertTrue(email_verification.exists())
        self.assertEquals(
            email_verification.first().expiration.date(),
            (now() + timedelta(hours=48)).date()
        )

    def test_user_registration_post_error(self):
        User.objects.create(username=self.data['username'])
        response = self.client.post(self.path, self.data)
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Пользователь с таким именем уже существует.', html=True)
