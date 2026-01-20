from django import forms
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse


def sample_json_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"ok": True})


def json_list_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"items": [{"id": 1}, {"id": 2}, {"id": 3}]})


def html_view(request: HttpRequest) -> HttpResponse:
    html = """<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
<h1>Hello World</h1>
<p>This is a test page with <strong>bold text</strong>.</p>
</body>
</html>"""
    return HttpResponse(html, content_type="text/html")


def plain_text_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Plain text content", content_type="text/plain")


def created_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"id": 1, "created": True}, status=201)


def accepted_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "processing"}, status=202)


def no_content_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status=204)


def redirect_view(request: HttpRequest) -> HttpResponse:
    return redirect("/json/")


def moved_permanently_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse(status=301)
    response["Location"] = "/json/"
    return response


def found_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse(status=302)
    response["Location"] = "/json/"
    return response


def see_other_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse(status=303)
    response["Location"] = "/json/"
    return response


def bad_request_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Bad request", status=400)


def unauthorized_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Unauthorized", status=401)


def forbidden_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Forbidden", status=403)


def not_found_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Not found", status=404)


def conflict_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Conflict", status=409)


def gone_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Gone", status=410)


def unprocessable_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Unprocessable", status=422)


def too_many_requests_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Too many requests", status=429)


def server_error_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Server error", status=500)


def custom_header_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("OK")
    response["X-Custom-Header"] = "custom-value"
    response["X-Another-Header"] = "contains-fragment-here"
    return response


def invalid_json_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("not valid json", content_type="application/json")


class SampleForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)


def template_view(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        "test_template.html",
        {"title": "Test Title", "items": ["a", "b", "c"]},
    )


def form_error_view(request: HttpRequest) -> TemplateResponse:
    form = SampleForm(data={"name": "", "email": "invalid"})
    form.is_valid()  # Trigger validation
    return TemplateResponse(
        request,
        "form_template.html",
        {"form": form},
    )


SampleFormSet = forms.formset_factory(SampleForm, extra=2)


def formset_error_view(request: HttpRequest) -> TemplateResponse:
    formset = SampleFormSet(
        data={
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-0-name": "",
            "form-0-email": "invalid",
            "form-1-name": "Test",
            "form-1-email": "test@example.com",
        }
    )
    formset.is_valid()  # Trigger validation
    return TemplateResponse(
        request,
        "formset_template.html",
        {"formset": formset},
    )


def payment_required_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Payment required", status=402)


def method_not_allowed_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Method not allowed", status=405)


def request_timeout_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Request timeout", status=408)


def service_unavailable_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Service unavailable", status=503)


def json_array_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse([{"id": 1}, {"id": 2}], safe=False)


def json_nested_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        {
            "user": {"id": 1, "name": "John", "profile": {"age": 30, "city": "NYC"}},
            "tags": ["python", "django"],
            "count": 42,
        }
    )


def session_set_view(request: HttpRequest) -> HttpResponse:
    request.session["user_id"] = 123
    request.session["username"] = "testuser"
    request.session["is_authenticated"] = True
    return HttpResponse("Session set")


def cookie_set_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookies set")
    response.set_cookie("session_id", "abc123")
    response.set_cookie("theme", "dark")
    return response


def cookie_expire_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie expired")
    response.delete_cookie("session_id")
    return response


def cookie_detailed_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie with details")
    response.set_cookie("detailed", "value", max_age=3600, path="/api/")
    response.set_cookie("maxage_only", "value", max_age=7200)
    return response


def streaming_csv_view(request: HttpRequest) -> HttpResponse:
    from django.http import StreamingHttpResponse

    def generate_csv():
        yield "Name,Email,Age\r\n"
        yield "John,john@example.com,30\r\n"
        yield "Jane,jane@example.com,25\r\n"
        yield "Bob,bob@example.com,35\r\n"

    response = StreamingHttpResponse(generate_csv(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="users.csv"'
    return response


def streaming_text_view(request: HttpRequest) -> HttpResponse:
    from django.http import StreamingHttpResponse

    def generate_text():
        yield "Line 1\n"
        yield "Line 2\n"
        yield "Line 3\n"

    return StreamingHttpResponse(generate_text(), content_type="text/plain")


def streaming_empty_view(request: HttpRequest) -> HttpResponse:
    from django.http import StreamingHttpResponse

    def generate_empty():
        yield ""

    return StreamingHttpResponse(generate_empty(), content_type="text/plain")


def download_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("file content here", content_type="application/octet-stream")
    response["Content-Disposition"] = 'attachment; filename="report.txt"'
    return response


def inline_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("inline content", content_type="text/plain")
