from __future__ import annotations

import sys

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

from django.http import HttpResponse


class DjangoDebugMixin:
    _response: HttpResponse

    def dump_session(self) -> Self:
        print("\n[Session Data]")
        if not hasattr(self._response, "wsgi_request"):
            print("  (no request context available)")
            return self
        session = dict(self._response.wsgi_request.session)
        if session:
            for key, value in session.items():
                print(f"  {key}: {value!r}")
        else:
            print("  (empty)")
        return self
