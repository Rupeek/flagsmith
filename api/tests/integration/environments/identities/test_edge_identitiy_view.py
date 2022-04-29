import urllib

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status

from environments.identities.views import EdgeIdentityViewSet


@pytest.fixture()
def dynamo_wrapper_mock(mocker):
    return mocker.patch(
        "environments.identities.models.Identity.dynamo_wrapper",
    )


def test_get_identites_returns_bad_request_if_dynamo_is_not_enabled(
    admin_client, environment, environment_api_key
):
    # Given
    url = reverse(
        "api-v1:environments:environment-edge-identities-list",
        args=[environment_api_key],
    )
    # When
    response = admin_client.get(url)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_identity(
    admin_client,
    dynamo_enabled_environment,
    environment_api_key,
    identity_document,
    dynamo_wrapper_mock,
):
    # Given
    identity_uuid = identity_document["identity_uuid"]

    url = reverse(
        "api-v1:environments:environment-edge-identities-detail",
        args=[environment_api_key, identity_uuid],
    )
    dynamo_wrapper_mock.get_item_from_uuid.return_value = identity_document
    # When
    response = admin_client.get(url)
    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["identity_uuid"] == identity_uuid
    dynamo_wrapper_mock.get_item_from_uuid.assert_called_with(
        environment_api_key, identity_uuid
    )


def test_get_identity_returns_404_if_identity_does_not_exists(
    admin_client,
    dynamo_enabled_environment,
    environment_api_key,
    dynamo_wrapper_mock,
):
    # Given
    url = reverse(
        "api-v1:environments:environment-edge-identities-detail",
        args=[environment_api_key, "identity_uuid_that_does_not_exists"],
    )
    dynamo_wrapper_mock.get_item_from_uuid.side_effect = ObjectDoesNotExist

    # When
    response = admin_client.get(url)

    # Then
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_identity(
    admin_client,
    dynamo_enabled_environment,
    environment_api_key,
    dynamo_wrapper_mock,
    identity_document,
):
    # Given
    identifier = identity_document["identifier"]
    composite_key = identity_document["composite_key"]
    url = reverse(
        "api-v1:environments:environment-edge-identities-list",
        args=[environment_api_key],
    )
    dynamo_wrapper_mock.get_item.return_value = None

    # When
    response = admin_client.post(url, data={"identifier": identifier})

    # Then, test that get_item was called to verify that identity does not exists already
    dynamo_wrapper_mock.get_item.assert_called_with(composite_key)

    # Next, let verify that put item was called with correct args
    name, args, _ = dynamo_wrapper_mock.mock_calls[1]
    assert name == "put_item"
    assert args[0]["identifier"] == identifier
    assert args[0]["composite_key"] == composite_key

    # Finally, let's verify the response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["identifier"] == identifier
    assert response.json()["identity_uuid"] is not None


def test_create_identity_returns_400_if_identity_already_exists(
    admin_client,
    dynamo_enabled_environment,
    environment_api_key,
    identity_document,
    dynamo_wrapper_mock,
):
    # Given
    identifier = identity_document["identifier"]

    url = reverse(
        "api-v1:environments:environment-edge-identities-list",
        args=[environment_api_key],
    )
    dynamo_wrapper_mock.get_item.return_value = identity_document  # {
    response = admin_client.post(url, data={"identifier": identifier})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_identity(
    admin_client,
    dynamo_enabled_environment,
    environment_api_key,
    identity_document,
    dynamo_wrapper_mock,
):
    # Given
    identity_uuid = identity_document["identity_uuid"]
    url = reverse(
        "api-v1:environments:environment-edge-identities-detail",
        args=[environment_api_key, identity_uuid],
    )

    dynamo_wrapper_mock.get_item_from_uuid.return_value = identity_document
    # When
    response = admin_client.delete(url)

    # Then
    assert response.status_code == status.HTTP_204_NO_CONTENT

    dynamo_wrapper_mock.get_item_from_uuid.assert_called_with(
        environment_api_key, identity_uuid
    )
    dynamo_wrapper_mock.delete_item.assert_called_with(
        identity_document["composite_key"]
    )


def test_identity_list_pagination(
    admin_client,
    dynamo_enabled_environment,
    environment_api_key,
    identity_document,
    dynamo_wrapper_mock,
):
    # Firstly, let's setup the data
    identity_item_key = {
        k: v
        for k, v in identity_document.items()
        if k in ["composite_key", "environment_api_key", "identifier"]
    }

    base_url = reverse(
        "api-v1:environments:environment-edge-identities-list",
        args=[environment_api_key],
    )
    url = f"{base_url}?page_size=1"
    dynamo_wrapper_mock.get_all_items.return_value = {
        "Items": [identity_document],
        "Count": 1,
        "LastEvaluatedKey": identity_item_key,
    }

    response = admin_client.get(url)
    # Next, Test the response
    assert response.status_code == 200
    response = response.json()
    assert response["previous"] is None

    # Fetch the next url from the response since LastEvaluatedKey was part of the response from dynamodb
    next_url = response["next"]

    # Make the call using the next url
    response = admin_client.get(next_url)

    # And verify that get_all_items was called with correct arguments
    dynamo_wrapper_mock.get_all_items.assert_called_with(
        environment_api_key, 1, identity_item_key
    )
    # And previous_url is same as last next_url
    assert response.status_code == 200
    assert response.json()["previous"] == next_url


def test_get_identities_list(
    admin_client,
    dynamo_enabled_environment,
    environment_api_key,
    identity_document,
    dynamo_wrapper_mock,
):
    # Given
    url = reverse(
        "api-v1:environments:environment-edge-identities-list",
        args=[environment_api_key],
    )

    dynamo_wrapper_mock.get_all_items.return_value = {
        "Items": [identity_document],
        "Count": 1,
    }

    # When
    response = admin_client.get(url)
    assert (
        response.json()["results"][0]["identifier"] == identity_document["identifier"]
    )
    assert len(response.json()["results"]) == 1

    # Then
    assert response.status_code == status.HTTP_200_OK
    dynamo_wrapper_mock.get_all_items.assert_called_with(environment_api_key, 999, None)


def test_search_identities_without_exact_match(
    admin_client,
    dynamo_enabled_environment,
    environment_api_key,
    identity_document,
    dynamo_wrapper_mock,
):
    # Given
    identifier = identity_document["identifier"]

    base_url = reverse(
        "api-v1:environments:environment-edge-identities-list",
        args=[environment_api_key],
    )

    url = "%s?q=%s" % (base_url, identifier)
    dynamo_wrapper_mock.search_items_with_identifier.return_value = {
        "Items": [identity_document],
        "Count": 1,
    }

    # When
    response = admin_client.get(url)
    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"][0]["identifier"] == identifier
    assert len(response.json()["results"]) == 1

    dynamo_wrapper_mock.search_items_with_identifier.assert_called_with(
        environment_api_key,
        identifier,
        EdgeIdentityViewSet.dynamo_identifier_search_functions["BEGINS_WITH"],
        999,
        None,
    )


def test_search_for_identities_with_exact_match(
    admin_client,
    dynamo_enabled_environment,
    environment_api_key,
    identity_document,
    dynamo_wrapper_mock,
):
    # Given
    identifier = identity_document["identifier"]

    base_url = reverse(
        "api-v1:environments:environment-edge-identities-list",
        args=[environment_api_key],
    )
    url = "%s?%s" % (
        base_url,
        urllib.parse.urlencode({"q": f'"{identifier}"'}),
    )
    dynamo_wrapper_mock.search_items_with_identifier.return_value = {
        "Items": [identity_document],
        "Count": 1,
    }

    # When
    response = admin_client.get(url)
    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"][0]["identifier"] == identifier
    assert len(response.json()["results"]) == 1

    dynamo_wrapper_mock.search_items_with_identifier.assert_called_with(
        environment_api_key,
        identifier,
        EdgeIdentityViewSet.dynamo_identifier_search_functions["EQUAL"],
        999,
        None,
    )
