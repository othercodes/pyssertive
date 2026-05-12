import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.mark.django_db
def test_assert_streaming_should_pass_when_response_is_streaming(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming()
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_should_raise_when_response_is_not_streaming(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected StreamingHttpResponse"):
        response.assert_streaming()


@pytest.mark.django_db
def test_assert_download_should_pass_when_response_has_attachment_disposition(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/download/")
    result = response.assert_download()
    assert result is response


@pytest.mark.django_db
def test_assert_download_should_pass_when_filename_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/download/")
    result = response.assert_download(filename="report.txt")
    assert result is response


@pytest.mark.django_db
def test_assert_download_should_raise_when_response_is_inline(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/inline/")
    with pytest.raises(AssertionError, match="Expected Content-Disposition: attachment"):
        response.assert_download()


@pytest.mark.django_db
def test_assert_download_should_raise_when_filename_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/download/")
    with pytest.raises(AssertionError, match=r"Expected filename 'wrong\.txt'"):
        response.assert_download(filename="wrong.txt")


@pytest.mark.django_db
def test_assert_streaming_contains_should_pass_when_text_is_in_stream(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_contains("Line 2")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_contains_should_raise_when_text_is_absent_from_stream(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected streaming content to contain"):
        response.assert_streaming_contains("not there")


@pytest.mark.django_db
def test_assert_streaming_not_contains_should_pass_when_text_is_absent_from_stream(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_not_contains("not there")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_not_contains_should_raise_when_text_is_in_stream(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected streaming content to NOT contain"):
        response.assert_streaming_not_contains("Line 2")


@pytest.mark.django_db
def test_assert_streaming_matches_should_pass_when_pattern_matches_stream(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-csv/")
    result = response.assert_streaming_matches(r"john@example\.com")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_matches_should_raise_when_pattern_does_not_match(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-csv/")
    with pytest.raises(AssertionError, match="Expected streaming content to match pattern"):
        response.assert_streaming_matches(r"notfound@example\.com")


@pytest.mark.django_db
def test_assert_streaming_line_count_should_pass_when_exact_count_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_line_count(exact=3)
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_line_count_should_raise_when_exact_count_mismatches(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected exactly 5 lines"):
        response.assert_streaming_line_count(exact=5)


@pytest.mark.django_db
def test_assert_streaming_line_count_should_pass_when_min_threshold_met(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_line_count(min=2)
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_line_count_should_raise_when_below_min_threshold(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected at least 10 lines"):
        response.assert_streaming_line_count(min=10)


@pytest.mark.django_db
def test_assert_streaming_line_count_should_pass_when_max_threshold_met(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_line_count(max=5)
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_line_count_should_raise_when_above_max_threshold(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected at most 1 lines"):
        response.assert_streaming_line_count(max=1)


@pytest.mark.django_db
def test_assert_streaming_empty_should_pass_when_stream_has_no_lines(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-empty/")
    result = response.assert_streaming_empty()
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_empty_should_raise_when_stream_has_lines(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Expected empty streaming content"):
        response.assert_streaming_empty()


@pytest.mark.django_db
def test_assert_streaming_csv_header_should_accept_columns_as_list(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-csv/")
    result = response.assert_streaming_csv_header(["Name", "Email", "Age"])
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_csv_header_should_accept_columns_as_comma_separated_string(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/streaming-csv/")
    result = response.assert_streaming_csv_header("Name,Email,Age")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_csv_header_should_raise_when_header_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-csv/")
    with pytest.raises(AssertionError, match="Expected CSV header"):
        response.assert_streaming_csv_header(["Wrong", "Headers"])


@pytest.mark.django_db
def test_assert_streaming_csv_header_should_raise_when_stream_is_empty(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-empty/")
    with pytest.raises(AssertionError, match="Expected CSV content but response is empty"):
        response.assert_streaming_csv_header(["Name"])


@pytest.mark.django_db
def test_assert_streaming_line_should_pass_when_first_line_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_line(0, "Line 1")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_line_should_pass_when_indexed_line_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    result = response.assert_streaming_line(1, "Line 2")
    assert result is response


@pytest.mark.django_db
def test_assert_streaming_line_should_raise_when_line_content_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Line 0: expected 'Wrong'"):
        response.assert_streaming_line(0, "Wrong")


@pytest.mark.django_db
def test_assert_streaming_line_should_raise_when_line_index_out_of_range(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-text/")
    with pytest.raises(AssertionError, match="Line index 10 out of range"):
        response.assert_streaming_line(10, "anything")


@pytest.mark.django_db
def test_streaming_assertions_should_also_work_on_regular_http_response(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/plain-text/")
    result = response.assert_streaming_contains("Plain text content")
    assert result is response


@pytest.mark.django_db
def test_assert_download_should_pass_when_streaming_response_is_attachment(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-csv/")
    result = response.assert_download(filename="users.csv")
    assert result is response


@pytest.mark.django_db
def test_streaming_assertions_should_return_self_for_method_chaining(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/streaming-csv/")
    result = (
        response.assert_ok()
        .assert_streaming()
        .assert_download(filename="users.csv")
        .assert_streaming_csv_header(["Name", "Email", "Age"])
        .assert_streaming_line_count(exact=4)
        .assert_streaming_contains("john@example.com")
    )
    assert result is response
