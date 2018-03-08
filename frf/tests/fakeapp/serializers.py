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

from frf import serializers

from frf.tests.fakeapp import models


class CompanySerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(
        model=models.Author, many=True)

    class Meta:
        model = models.Company
        fields = ('id', 'name', 'authors')


class CompanySerializerV2(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(
        model=models.Author, many=True,
    )

    class Meta:
        model = models.Company
        fields = ('id', 'name', 'authors')


class CompanySerializerV3(serializers.ModelSerializer):
    authors = serializers.HyperlinkedRelatedField(
        model=models.Author, many=True,
        template_uri='/api/v1/authors/{uuid1}',
    )

    class Meta:
        model = models.Company
        fields = ('id', 'name', 'authors')


class AuthorSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        model=models.Company)
    books = serializers.PrimaryKeyRelatedField(
        model=models.Book, many=True)

    class Meta:
        fields = ('uuid1', 'uuid2', 'name', 'company', 'books')
        model = models.Author


class CompanySerializerV4(serializers.ModelSerializer):
    authors = serializers.SerializerField(
        serializer=AuthorSerializer,
        many=True,
    )

    class Meta:
        model = models.Company
        fields = ('id', 'name', 'authors')


class BookSerialzier(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        model=models.Author)

    class Meta:
        fields = ('id', 'title', 'author')
        model = models.Book
