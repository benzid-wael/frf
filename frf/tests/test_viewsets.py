# Copyright 2016 by Teem, and other contributors,
# as noted in the individual source code files.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By contributing to this project, you agree to also license your source
# code under the terms of the Apache License, Version 2.0, as described
# above.

import functools
import json
import uuid

import falcon

from falcon.testing import TestCase as BaseTestCase

from frf import exceptions, filters, renderers, serializers, viewsets
from frf.tests.fake import faker

ITEMS = []


class User(object):
    pass


class SimpleKeyAuthentication(object):
    def authenticate(self, req, view):
        key = req.get_param('auth_key')
        if key != 'superpassword':
            raise exceptions.HTTPUnauthorized(
                title='Not Authorized',
                description='Not Authorized',
                challenges=('key',))

        return User()


def awesome_flag_present(req=None, qs=None, is_awesome=False, **kwargs):
    new_qs = []
    for item in qs:
        if item.is_awesome == is_awesome:
            new_qs.append(item)
    return new_qs


class DummySerializer(serializers.Serializer):
    uuid = serializers.UUIDField(default=uuid.uuid4)
    name = serializers.StringField(required=True)
    email = serializers.EmailField(required=True)
    title = serializers.StringField(max_length=1000)
    is_awesome = serializers.BooleanField(required=False, default=True)


class IsAwesomeFlagFilter(filters.CompoundFilter):
    def __init__(self):
        super().__init__(filters=[
            filters.FlagFilter(
                flag='is_awesome',
                filter_flag_present_func=functools.partial(
                    awesome_flag_present, is_awesome=True,
                    model_field=DummySerializer.is_awesome)),

            filters.FlagFilter(
                flag='is_not_awesome',
                filter_flag_present_func=functools.partial(
                    awesome_flag_present, is_awesome=False,
                    model_field=DummySerializer.is_awesome)),
            ])


class DummyViewSet(viewsets.ViewSet):
    filters = [IsAwesomeFlagFilter()]
    renderers = [renderers.ListMetaRenderer()]
    serializer = DummySerializer()
    authentication = [SimpleKeyAuthentication()]

    def get_obj(self, req, **kwargs):
        for item in ITEMS:
            if str(item.uuid) == str(kwargs.get('uuid')):
                return item

    def create_save_obj(self, req, obj, **kwargs):
        ITEMS.append(obj)

    def update_save_obj(self, req, obj, **kwargs):
        pass

    def delete_remove_obj(self, req, obj, **kwargs):
        to_delete = []

        for item in ITEMS:
            if str(item.uuid) == str(obj.uuid):
                to_delete.append(item)

        for item in to_delete:
            ITEMS.remove(item)

    def get_qs(self, req, **kwargs):
        return ITEMS


class TestCase(BaseTestCase):
    def setUp(self):
        global ITEMS
        super().setUp()

        self.api = falcon.API()
        self.viewset = DummyViewSet()
        self.api.add_route('/dummies/', self.viewset)
        self.api.add_route('/dummies/{uuid}/', self.viewset)
        ITEMS = []

        serializer = self.viewset.serializer
        # add 3 test objects
        for i in range(3):
            data = {
                'name': faker.name(),
                'email': faker.email(),
                'title': faker.sentence(nb_words=5),
                'is_awesome': i % 2 == 0,
                }

            obj = serializer.save(data=data)
            ITEMS.append(obj)

    def test_index(self):
        res = self.simulate_get(
            '/dummies/', query_string='auth_key=superpassword')

        json = res.json

        self.assertEquals(json['meta']['total'], 3)
        self.assertEquals(len(json['results']), 3)

        for item in json['results']:
            self.assertEqual(5, len(item))
            self.assertIsInstance(item['uuid'], str)
            self.assertEqual(len(str(uuid.uuid4())), len(item['uuid']))
            self.assertIsInstance(item['email'], str)
            self.assertIn('@', item['email'])
            self.assertIsInstance(item['title'], str)
            self.assertIsInstance(item['is_awesome'], bool)

    def test_index_filter_is_awesome(self):
        res = self.simulate_get(
            '/dummies/',
            query_string='auth_key=superpassword&filter=is_awesome')

        json = res.json

        self.assertEquals(json['meta']['total'], 2)
        self.assertEquals(len(json['results']), 2)

        for item in json['results']:
            self.assertTrue(item['is_awesome'])

    def test_index_filter_is_not_awesome(self):
        res = self.simulate_get(
            '/dummies/',
            query_string='auth_key=superpassword&filter=is_not_awesome')

        json = res.json

        self.assertEquals(json['meta']['total'], 1)
        self.assertEquals(len(json['results']), 1)

        for item in json['results']:
            self.assertFalse(item['is_awesome'])

    def test_retrieve(self):
        item = ITEMS[0]

        res = self.simulate_get(
            '/dummies/{}/'.format(item.uuid),
            query_string='auth_key=superpassword')

        item = res.json

        self.assertEqual(5, len(item))
        self.assertIsInstance(item['uuid'], str)
        self.assertEqual(len(str(uuid.uuid4())), len(item['uuid']))
        self.assertIsInstance(item['email'], str)
        self.assertIn('@', item['email'])
        self.assertIsInstance(item['title'], str)
        self.assertIsInstance(item['is_awesome'], bool)
        self.assertTrue(item['is_awesome'])

    def test_create(self):
        current_count = len(ITEMS)
        create_data = {
            'email': faker.email(),
            'name': faker.name(),
            'title': faker.sentence(),
            'is_awesome': True,
        }

        res = self.simulate_post(
            '/dummies/',
            body=json.dumps(create_data),
            query_string='auth_key=superpassword')

        self.assertEqual(res.status, falcon.HTTP_201)

        item = res.json

        self.assertEqual(5, len(item))
        self.assertIsInstance(item['uuid'], str)
        self.assertEqual(len(str(uuid.uuid4())), len(item['uuid']))
        self.assertIsInstance(item['email'], str)
        self.assertIn('@', item['email'])
        self.assertIsInstance(item['title'], str)
        self.assertIsInstance(item['is_awesome'], bool)
        self.assertTrue(item['is_awesome'])

        self.assertTrue(len(ITEMS), current_count)

    def test_destroy(self):
        current_count = len(ITEMS)
        item = ITEMS[0]

        res = self.simulate_delete(
            '/dummies/{}/'.format(item.uuid),
            query_string='auth_key=superpassword')

        self.assertEqual(res.status, falcon.HTTP_204)
        self.assertTrue(current_count > len(ITEMS))
        self.assertFalse(item in ITEMS)

    def test_update(self):
        item = ITEMS[0]

        update_data = {'email': faker.email()}

        res = self.simulate_patch(
            '/dummies/{}/'.format(item.uuid),
            body=json.dumps(update_data),
            query_string='auth_key=superpassword')

        self.assertEqual(res.status, falcon.HTTP_204)

        item = ITEMS[0]
        self.assertEqual(item.email, update_data['email'])

    def test_fail_unauthorized(self):
        res = self.simulate_get('/dummies/')
        self.assertEqual(res.status, falcon.HTTP_401)

    def test_fail_method_not_allowed(self):
        self.viewset.allowed_actions = ('list',)

        item = ITEMS[0]

        update_data = {'email': faker.email()}

        res = self.simulate_patch(
            '/dummies/{}/'.format(item.uuid),
            body=json.dumps(update_data),
            query_string='auth_key=superpassword')

        self.assertEqual(res.status, falcon.HTTP_405)
