import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.fixture
def fluent_admin_client(admin_client):
    return FluentHttpAssertClient(admin_client)
