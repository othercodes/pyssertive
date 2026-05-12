import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from pyssertive.adapters.django.db import (
    assert_model_count,
    assert_model_exists,
    assert_model_not_exists,
    assert_model_soft_deleted,
    assert_num_queries,
    assert_queryset_equal,
)
from tests.app.models import SoftDeleteModel


@pytest.mark.django_db
def test_assert_model_exists_should_pass_when_model_present():
    User.objects.create(username="demo")
    assert_model_exists(User, username="demo")


@pytest.mark.django_db
def test_assert_model_exists_should_raise_when_model_absent():
    with pytest.raises(AssertionError, match="does not exist"):
        assert_model_exists(User, username="nonexistent")


@pytest.mark.django_db
def test_assert_model_not_exists_should_pass_when_model_absent():
    assert_model_not_exists(User, username="nope")


@pytest.mark.django_db
def test_assert_model_not_exists_should_raise_when_model_present():
    User.objects.create(username="demo")
    with pytest.raises(AssertionError, match="unexpectedly exists"):
        assert_model_not_exists(User, username="demo")


@pytest.mark.django_db
def test_assert_model_count_should_pass_when_count_matches():
    User.objects.create(username="demo")
    assert_model_count(User, 1)


@pytest.mark.django_db
def test_assert_model_count_should_raise_when_count_mismatches():
    User.objects.create(username="demo")
    with pytest.raises(AssertionError, match="Expected 5 records"):
        assert_model_count(User, 5)


@pytest.mark.django_db
def test_assert_queryset_equal_should_pass_when_querysets_match():
    User.objects.create(username="user1")
    User.objects.create(username="user2")
    users = User.objects.all().order_by("username")
    assert_queryset_equal(users, ["<User: user1>", "<User: user2>"])


@pytest.mark.django_db
def test_assert_queryset_equal_should_raise_when_querysets_differ():
    User.objects.create(username="user1")
    users = User.objects.all()
    with pytest.raises(AssertionError):
        assert_queryset_equal(users, ["<User: wrong>"])


@pytest.mark.django_db
def test_assert_num_queries_should_pass_when_query_count_matches():
    User.objects.create(username="demo")
    with assert_num_queries(1):
        list(User.objects.all())


@pytest.mark.django_db
def test_assert_num_queries_should_raise_when_query_count_mismatches():
    User.objects.create(username="demo")
    with pytest.raises(AssertionError, match="Expected 0 queries"), assert_num_queries(0):
        list(User.objects.all())


@pytest.mark.django_db
def test_assert_model_soft_deleted_should_raise_when_model_absent():
    with pytest.raises(AssertionError, match="does not exist"):
        assert_model_soft_deleted(User, username="nonexistent")


@pytest.mark.django_db
def test_assert_model_soft_deleted_should_raise_when_model_has_no_deleted_at_field():
    User.objects.create(username="demo")
    with pytest.raises(AssertionError, match="has no 'deleted_at' field"):
        assert_model_soft_deleted(User, username="demo")


@pytest.mark.django_db
def test_assert_model_soft_deleted_should_raise_when_model_is_not_deleted():
    SoftDeleteModel.objects.create(name="test")
    with pytest.raises(AssertionError, match="is not soft deleted"):
        assert_model_soft_deleted(SoftDeleteModel, name="test")


@pytest.mark.django_db
def test_assert_model_soft_deleted_should_pass_when_model_is_deleted():
    SoftDeleteModel.objects.create(name="test", deleted_at=timezone.now())
    assert_model_soft_deleted(SoftDeleteModel, name="test")
