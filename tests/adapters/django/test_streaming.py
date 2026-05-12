import pytest


@pytest.mark.django_db
def test_assert_streaming(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming()
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_fails_for_non_streaming(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected StreamingHttpResponse"):
        response.assert_streaming()


@pytest.mark.django_db
def test_assert_download(fluent_admin_client):
    response = fluent_admin_client.get("/download/")
    result = response.assert_download()
    assert result is response


@pytest.mark.django_db
def test_assert_download_with_filename(fluent_admin_client):
    response = fluent_admin_client.get("/download/")
    result = response.assert_download(filename="report.txt")
    assert result is response


@pytest.mark.django_db
def test_assert_download_fails_without_attachment(fluent_admin_client):
    response = fluent_admin_client.get("/inline/")
    with pytest.raises(AssertionError, match="Expected Content-Disposition: attachment"):
        response.assert_download()


@pytest.mark.django_db
def test_assert_download_fails_with_wrong_filename(fluent_admin_client):
    response = fluent_admin_client.get("/download/")
    with pytest.raises(AssertionError, match=r"Expected filename 'wrong\.txt'"):
        response.assert_download(filename="wrong.txt")


@pytest.mark.django_db
def test_assert_streaming_contains(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_contains("Line 2")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_contains_fails(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected streaming content to contain"):
        response.assert_streaming_contains("not there")


@pytest.mark.django_db
def test_assert_streaming_not_contains(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_not_contains("not there")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_not_contains_fails(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected streaming content to NOT contain"):
        response.assert_streaming_not_contains("Line 2")


@pytest.mark.django_db
def test_assert_streaming_matches(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-csv/")
    result = response.assert_streaming_matches(r"john@example\.com")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_matches_fails(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-csv/")
    with pytest.raises(AssertionError, match="Expected streaming content to match pattern"):
        response.assert_streaming_matches(r"notfound@example\.com")


@pytest.mark.django_db
def test_assert_streaming_line_count_exact(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_line_count(exact=3)
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_line_count_exact_fails(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected exactly 5 lines"):
        response.assert_streaming_line_count(exact=5)


@pytest.mark.django_db
def test_assert_streaming_line_count_min(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_line_count(min=2)
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_line_count_min_fails(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected at least 10 lines"):
        response.assert_streaming_line_count(min=10)


@pytest.mark.django_db
def test_assert_streaming_line_count_max(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_line_count(max=5)
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_line_count_max_fails(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected at most 1 lines"):
        response.assert_streaming_line_count(max=1)


@pytest.mark.django_db
def test_assert_streaming_empty(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-empty/")
    result = response.assert_streaming_empty()
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_empty_fails(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected empty streaming content"):
        response.assert_streaming_empty()


@pytest.mark.django_db
def test_assert_streaming_csv_header_with_list(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-csv/")
    result = response.assert_streaming_csv_header(["Name", "Email", "Age"])
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_csv_header_with_string(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-csv/")
    result = response.assert_streaming_csv_header("Name,Email,Age")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_csv_header_fails(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-csv/")
    with pytest.raises(AssertionError, match="Expected CSV header"):
        response.assert_streaming_csv_header(["Wrong", "Headers"])


@pytest.mark.django_db
def test_assert_streaming_csv_header_fails_empty(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-empty/")
    with pytest.raises(AssertionError, match="Expected CSV content but response is empty"):
        response.assert_streaming_csv_header(["Name"])


@pytest.mark.django_db
def test_assert_streaming_line(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_line(0, "Line 1")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_line_second(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_line(1, "Line 2")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_line_fails_wrong_content(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Line 0: expected 'Wrong'"):
        response.assert_streaming_line(0, "Wrong")


@pytest.mark.django_db
def test_assert_streaming_line_fails_out_of_range(fluent_admin_client):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Line index 10 out of range"):
        response.assert_streaming_line(10, "anything")


@pytest.mark.django_db
def test_streaming_content_from_non_streaming_response(fluent_admin_client):
    """Test that _get_streaming_content works with regular HttpResponse too."""
    response = fluent_admin_client.get("/plain-text/")
    result = response.assert_streaming_contains("Plain text content")
    assert result is response


@pytest.mark.django_db
def test_streaming_download_with_streaming_response(fluent_admin_client):
    """Test assert_download works with streaming responses."""
    response = fluent_admin_client.get("/streaming-csv/")
    result = response.assert_download(filename="users.csv")
    assert result is response


@pytest.mark.django_db
def test_chained_streaming_assertions(fluent_admin_client):
    """Test that streaming assertions can be chained fluently."""
    response = fluent_admin_client.get("/streaming-csv/")
    result = (
        response.assert_ok()
        .assert_streaming()
        .assert_download(filename="users.csv")
        .assert_streaming_csv_header(["Name", "Email", "Age"])
        .assert_streaming_line_count(exact=4)  # header + 3 data rows
        .assert_streaming_contains("john@example.com")
    )
    assert result is response
