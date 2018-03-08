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

from frf.tests.fakeapp import viewsets

book_viewset = viewsets.BookViewSet()
author_viewset = viewsets.AuthorViewSet()
# 1st version using PrimaryKeyRelatedField
company_viewset = viewsets.CompanyViewSet()
# 2nd version using StringRelatedField
company_viewset_v2 = viewsets.CompanyViewSetV2()
# 3rd version using HyperlinkedRelateField
company_viewset_v3 = viewsets.CompanyViewSetV3()
# 4th version using SerializerField
company_viewset_v4 = viewsets.CompanyViewSetV4()


urlpatterns = [
    ('/companies/', company_viewset),
    ('/companies/{id}/', company_viewset),
    ('/v2/companies/', company_viewset_v2),
    ('/v3/companies/', company_viewset_v3),
    ('/v4/companies/', company_viewset_v4),
    ('/books/', book_viewset),
    ('/books/{id}/', book_viewset),
    ('/authors/', author_viewset),
    ('/authors/{uuid1}/{uuid2}/', author_viewset),
    ('/test_permissions_view/', viewsets.TestView()),
    ]
