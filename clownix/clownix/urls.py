"""URL-конфигурация проекта clownix."""

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from blog.sitemaps import CategorySitemap, PostSitemap, StaticViewSitemap
from blog.views_robots import robots_txt

sitemaps = {
    "static": StaticViewSitemap,
    "categories": CategorySitemap,
    "posts": PostSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt, name="robots_txt"),
    path('sitemap.xml', sitemap, {"sitemaps": sitemaps},
         name="django.contrib.sitemaps.views.sitemap"),
    path('', include("blog.urls")),
]

# Раздача загруженных картинок (cover, inline) в режиме разработки.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
