"""Динамическая выдача robots.txt со ссылкой на sitemap.xml."""

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_GET


_PROD_HOSTS = {"clownix.ru", "www.clownix.ru"}


@require_GET
def robots_txt(request):
    """Сгенерировать robots.txt для текущего хоста с директивой Sitemap."""
    host = request.get_host().split(":")[0] or "clownix.ru"
    scheme = "https" if host in _PROD_HOSTS or request.is_secure() else request.scheme
    sitemap_url = f"{scheme}://{host}/sitemap.xml"

    lines = [
        "User-Agent: *",
        "Disallow: /admin/",
        "Disallow: /search/?",
        "Allow: /",
        "",
        f"Sitemap: {sitemap_url}",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
