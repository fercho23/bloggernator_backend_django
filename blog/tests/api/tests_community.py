
import json

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from blog.models.Community import Community
from blog.models.User import User

from blog.serializers.CommunitySerializer import CommunityModelSerializer

# list_community (filters)

class CommunityTests(TestCase):
    """ Test module for Community model """

    fixtures = [
        'user',
        'group',
        'community',
    ]

    def test_community_list(self):
        """ Community List """

        client = APIClient()
        response = client.get('/api/community/list/')
        result = json.loads(response.content)

        objects_query = Community.objects.select_related('owner').prefetch_related('members')
        objects_count = objects_query.count()
        objects = objects_query.all()[:10]
        serialization = CommunityModelSerializer(objects, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result.get('count', None), objects_count)
        self.assertEqual(result.get('results', None), serialization)
        self.assertIn('next', result)
        self.assertIn('previous', result)

    def test_community_list_second_page(self):
        """ Community List second Page"""

        data = {
            'page': 2,
        }

        client = APIClient()
        response = client.get('/api/community/list/', data)
        result = json.loads(response.content)

        objects_query = Community.objects.select_related('owner').prefetch_related('members')
        objects_count = objects_query.count()
        objects = objects_query.all()[10:20]
        serialization = CommunityModelSerializer(objects, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result.get('count', None), objects_count)
        self.assertEqual(result.get('results', None), serialization)
        self.assertIn('next', result)
        self.assertIn('previous', result)

    def test_community_create(self):
        """ Community Create """

        user = User.objects.get(pk=3)
        data = {
            'name': 'Testing Company',
            'detail': 'Detail Testing Company',
        }

        client = APIClient()
        client.force_authenticate(user)

        response = client.post('/api/community/create/', data)
        result = json.loads(response.content)

        community = Community.objects.filter(name=data['name']).first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(community)
        self.assertEqual(community.owner, user)
        self.assertEqual(community.name, data['name'])
        self.assertEqual(community.detail, data['detail'])

    def test_community_update(self):
        """ Community Update """

        community = Community.objects.get(pk=2)
        user = community.owner

        data = {
            'name': community.name + ' 2',
            'detail': community.detail[:50],
        }

        client = APIClient()
        client.force_authenticate(user)

        response = client.patch('/api/community/{}/update/'.format(community.uuid), data)
        result = json.loads(response.content)

        community = Community.objects.get(pk=community.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(community)
        self.assertEqual(community.name, data['name'])
        self.assertEqual(community.detail, data['detail'])

    def test_community_update_only_owner(self):
        """ Community Update only by Owner"""

        community = Community.objects.get(pk=2)
        user = User.objects.get(pk=4)

        data = {
            'name': 'Testing Company 2',
            'detail': 'Detail Testing Company 2',
        }

        client = APIClient()
        client.force_authenticate(user)

        response = client.patch('/api/community/{}/update/'.format(community.uuid), data)
        result = json.loads(response.content)

        community = Community.objects.filter(name=data['name']).first()
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', result)

    def test_community_delete(self):
        """ Community Delete """

        community = Community.objects.get(pk=2)
        user = community.owner

        client = APIClient()
        client.force_authenticate(user)

        response = client.delete('/api/community/{}/delete/'.format(community.uuid))

        community = Community.objects.filter(id=community.id).first()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(community)

    def test_community_delete_only_owner(self):
        """ Community Delete only by Owner"""

        community = Community.objects.get(pk=2)
        user = User.objects.get(pk=4)

        client = APIClient()
        client.force_authenticate(user)

        response = client.delete('/api/community/{}/delete/'.format(community.uuid))
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', result)

    def test_community_can_not_be_deleted_if_has_members(self):
        """ Community can not be deleted if it has members """

        community = Community.objects.get(pk=1)
        user = community.owner

        client = APIClient()
        client.force_authenticate(user)

        response = client.delete('/api/community/{}/delete/'.format(community.uuid))
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', result)