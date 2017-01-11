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
company_viewset = viewsets.CompanyViewSet()


routes = [
    ('/companies/', company_viewset),
    ('/companies/{id}/', company_viewset),
    ('/books/', book_viewset),
    ('/books/{id}/', book_viewset),
    ('/authors/', author_viewset),
    ('/authors/{uuid1}/{uuid2}/', author_viewset),
    ('/test_permissions_view/', viewsets.TestView()),
    ]
