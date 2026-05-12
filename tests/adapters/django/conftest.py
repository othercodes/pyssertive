import pytest
from django.test.client import Client

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.fixture
def fluent_admin_client(admin_client: Client) -> FluentHttpAssertClient:
    return FluentHttpAssertClient(admin_client)
