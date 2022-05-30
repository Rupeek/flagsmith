import typing
from typing import Iterable

import boto3
from boto3.dynamodb.conditions import Key
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from flag_engine.django_transform.document_builders import (
    build_identity_document,
)

if typing.TYPE_CHECKING:
    from environments.identities.models import Identity


class DynamoIdentityWrapper:
    def __init__(self):
        self._table = None
        if settings.IDENTITIES_TABLE_NAME_DYNAMO:
            self._table = boto3.resource("dynamodb").Table(
                settings.IDENTITIES_TABLE_NAME_DYNAMO
            )

    @property
    def is_enabled(self) -> bool:
        return self._table is not None

    def query_items(self, *args, **kwargs):
        return self._table.query(*args, **kwargs)

    def put_item(self, identity_dict: dict):
        self._table.put_item(Item=identity_dict)

    def write_identities(self, identities: Iterable["Identity"]):
        with self._table.batch_writer() as batch:
            for identity in identities:
                identity_document = build_identity_document(identity)
                batch.put_item(Item=identity_document)

    def get_item(self, composite_key: str) -> typing.Optional[dict]:
        return self._table.get_item(Key={"composite_key": composite_key}).get("Item")

    def delete_item(self, composite_key: str):
        self._table.delete_item(Key={"composite_key": composite_key})

    def get_item_from_uuid(self, environment_api_key: str, uuid: str):
        filter_expression = Key("identity_uuid").eq(uuid)
        query_kwargs = {
            "IndexName": "identity_uuid-index",
            "Limit": 1,
            "KeyConditionExpression": filter_expression,
        }
        try:
            return self.query_items(**query_kwargs)["Items"][0]
        except IndexError:
            raise ObjectDoesNotExist()

    def get_all_items(
        self, environment_api_key: str, limit: int, start_key: dict = None
    ):
        filter_expression = Key("environment_api_key").eq(environment_api_key)
        query_kwargs = {
            "IndexName": "environment_api_key-identifier-index",
            "Limit": limit,
            "KeyConditionExpression": filter_expression,
        }
        if start_key:
            query_kwargs.update(ExclusiveStartKey=start_key)
        return self.query_items(**query_kwargs)

    def search_items_with_identifier(
        self,
        environment_api_key: str,
        identifier: str,
        search_function: typing.Callable,
        limit: int,
        start_key: dict = None,
    ):
        filter_expression = Key("environment_api_key").eq(
            environment_api_key
        ) & search_function(identifier)
        query_kwargs = {
            "IndexName": "environment_api_key-identifier-index",
            "Limit": limit,
            "KeyConditionExpression": filter_expression,
        }
        if start_key:
            query_kwargs.update(ExclusiveStartKey=start_key)
        return self.query_items(**query_kwargs)
