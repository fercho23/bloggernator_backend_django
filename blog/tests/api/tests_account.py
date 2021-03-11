
from PIL import Image
import tempfile
import json

from django.test import TestCase

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.test import APIClient

from blog.models.User import User

from blog.serializers.UserSerializer import UserModelSerializer

# logout


class AccountTests(TestCase):
    """ Test module for Account actions """

    fixtures = [
        'user',
    ]

    def test_signup_user(self):
        """ Create an user """

        image = Image.new('RGB', (100, 100))

        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)

        data = {
            'email': 'user1@bloggernator.com',
            'username': 'user1',
            'password': 'Blog12345',
            'password_confirmation': 'Blog12345',
            'photo': tmp_file,
        }

        client = APIClient()
        response = client.post('/api/account/signup/', data, format='multipart')
        result = json.loads(response.content)

        obj = User.objects.filter(email=data['email']).first()
        serialization = UserModelSerializer(obj).data

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(result.get('user', None), serialization)
        self.assertIn('token', result)


    def test_login_user(self):
        """ Login """

        obj = User.objects.get(pk=2)
        data = {
            'email': obj.email,
            'password': 'Blog12345',
        }

        client = APIClient()
        response = client.post('/api/account/login/', data, format='json')
        result = json.loads(response.content)

        serialization = UserModelSerializer(obj).data

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(result.get('user', None), serialization)
        self.assertIn('token', result)

    def test_login_user_get_validation_error(self):
        """ Login with an incorrect password get Validation Error """

        obj = User.objects.get(pk=2)
        data = {
            'email': obj.email,
            'password': obj.email,
        }

        client = APIClient()
        response = client.post('/api/account/login/', data, format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', result)
