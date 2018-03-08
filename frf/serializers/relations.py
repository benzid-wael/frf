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

from gettext import gettext as _

import uuid
import six

from frf import exceptions
from .fields import Field


class RelatedField(Field):
    """Represent objects as a list of related keys.

    Requires that you use this field on a
    :class:`frf.serializers.ModelSerializer`

    For example:

    .. code-block:: python
       :caption: serializers.py

       from frf import serializers
       from myproject import models


       class AuthorSerializer(frf.ModelSerializer):
           name = serializers.StringField()
           books = serializers.PrimaryKeyRelatedField(
               model=models.Book, many=True)

    Will produce output something like this:

    .. code-block:: text

        {"name": "Dean Koontz", "books": [1, 2, 3, 4]}
    """
    requires_model_serializer = True
    MESSAGES = {
        'multikey': _('The table {table} has a composite primary key. You '
                      'must submit all keys in the format {{"key1": value1, '
                      '"key2": "value2"}}'),
    }

    def __init__(self, model, queryset=None, many=False, *args, **kwargs):
        """
        Args:
            model (frf.serializers.model.Model): The related model.
            queryset (sqlalchemy.orm.Query): The query.  If not specified,
                ``model.query.filter()`` will be used.
            many (boolean): Set to true if this relationship is a many-to-one
                or many-to-many relationship.
        """
        self.model = model
        self.many = many
        self._queryset = queryset

        super().__init__(*args, **kwargs)

    @property
    def queryset(self):
        if not hasattr(self.model, 'query'):
            raise exceptions.InitializationError(
                'Error initializing field {}, '
                'Invalid model {} or database is not initialized.'.format(
                    self.__class__.__name__,
                    self.model
                )
            )

        if not self._queryset:
            return self.model.query.filter()
        return self._queryset

    def get_primary_keys(self):
        mapper = self.model.__mapper__
        keys = [
            mapper.get_property_by_column(column).key
            for column in mapper.primary_key
        ]

        return keys[0] if len(keys) == 1 else keys

    def build_lookup(self, keys, item):
        lookup = {}

        if isinstance(keys, (list, tuple)):
            for key in keys:
                lookup[key] = item[key]
        else:
            lookup = {keys: item}

        return lookup

    def validate_ids(self, obj, data, value, ctx=None):
        keys = self.get_primary_keys()
        retval = None

        if value:
            if self.many:
                retval = self.get_items_many(value, validate=True, ctx=ctx)
            else:
                retval = self.get_item_single(value, validate=True, ctx=ctx)

        if not retval and value:
            raise exceptions.ValidationError(
                _('A row with the key "{key}" does'
                  ' not exist in the database.'.format(key=keys))
            )

    def get_items_many(self, value, validate=False, ctx=None):
        """Create a list of referenced items.

        Args:
            value (list): The ids. Must be a list of IDS. Each ID can be a
                single ID or a dictionary of IDS in the case of a composite
                primary key.
            validate (boolean): Set to ``True`` if you are calling this method
                from the validation step.  In the case of errors, a
                ``ValidationError`` will be raised.
        """
        items = []
        keys = self.get_primary_keys()
        for item in value:
            if not isinstance(keys, (list, tuple)):
                items.append(
                    self.queryset.filter_by(**{keys: item}).first()
                )
            else:
                if validate:
                    if not isinstance(item, dict):
                        raise exceptions.ValidationError(
                            self.MESSAGES['multikey'].format(
                                table=self.model.__tablename__,
                            )
                        )
                items.append(
                    self.queryset.filter_by(
                        **self.build_lookup(keys, item)).first()
                )
        return items

    def get_item_single(self, value, validate=False, ctx=None):
        """Get a single referenced item.

        Args:
            value (object): The id. The ID can be a single ID or a dictionary
                of IDS in the case of a composite primary key.
            validate (boolean): Set to ``True`` if you are calling this method
                from the validation step.  In the case of errors, a
                ``ValidationError`` will be raised.
        """
        item = None
        keys = self.get_primary_keys()
        if not isinstance(keys, list):
            item = self.queryset.filter_by(**{keys: value}).first()
        else:
            if validate:
                if not isinstance(value, dict):
                    raise exceptions.ValidationError(
                        self.MESSAGES['multikey'].format(
                            table=self.model.__tablename__,
                        )
                    )
            item = self.queryset.filter_by(
                **self.build_lookup(keys, value)
            ).first()

        return item

    def _serialize_value(self, value):
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    def serialize_primary_keys(self, obj):
        keys = self.get_primary_keys()
        if not isinstance(keys, (list, tuple)):
            values = getattr(obj, keys, None)
            values = self._serialize_value(values)
        else:
            values = {
                key: self._serialize_value(getattr(obj, key, None))
                for key in keys
            }
        return values

    def _serialize_single_item(self, value):
        return self.serialize_primary_keys(value)

    def serialize_single_item(self, obj, value):
        return self._serialize_single_item(value)

    def serialze_many_items(self, obj, values):
        return [self.serialize_single_item(obj, value) for value in values]

    def to_data(self, obj, value, ctx=None):
        if self.many:
            return self.serialze_many_items(obj, value)
        else:
            return self.serialize_single_item(obj, value)

    def to_python(self, obj, data, value, ctx=None):
        if value:
            if self.many:
                value = self.get_items_many(value, ctx=ctx)
            else:
                value = self.get_item_single(value, ctx=ctx)

        return value


class StringRelatedField(RelatedField):
    """
    A read only field that represents its targets using their
    plain string representation.
    """

    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        super(StringRelatedField, self).__init__(**kwargs)

    def _serialize_single_item(self, value):
        return six.text_type(value)


class PrimaryKeyRelatedField(RelatedField):
    pass


class PkOnlyRelatedField(RelatedField):
    MESSAGES = {
        'required': _('This field is required.'),
        'does_not_exist': _(
            'Invalid pk "{pk_value}" - object does not exist.',
        ),
        'incorrect_type': _(
            'Incorrect type. Expected pk value, received {data_type}.',
        ),
    }

    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop('pk_field', None)
        if not self.pk_field:
            raise exceptions.ValidationError(self.MESSAGES['required'])
        self.validate_primary_key()
        super(PkOnlyRelatedField, self).__init__(**kwargs)

    def validate_primary_key(self):
        mapper = self.model.__mapper__
        pk_field = [
            mapper.get_property_by_column(column).key
            for column in mapper.columns
        ]
        if pk_field:
            pk_field = pk_field[0]

        if not pk_field:
            raise exceptions.ValidationError(
                self.MESSAGES['does_not_exist'], self.pk_field,
            )
        elif not (pk_field.primary_key or pk_field.unique):
            raise exceptions.ValidationError(
                self.MESSAGES['incorrect_type'], pk_field.type_.__name__,
            )

    def get_primary_keys(self):
        self.validate_primary_key()
        return self.pk_field


class HyperlinkedRelatedField(RelatedField):

    def __init__(self, template_uri, context=None, **kwargs):
        self.template_uri = template_uri
        self.context = context or {}
        kwargs['read_only'] = True
        super(HyperlinkedRelatedField, self).__init__(**kwargs)

    def get_template_context(self, **kwargs):
        context = self.context.copy()
        context.update(kwargs)
        return context

    def _serialize_single_item(self, value):
        context = self.get_template_context(**value.__dict__)
        return self.template_uri.format(**context)
