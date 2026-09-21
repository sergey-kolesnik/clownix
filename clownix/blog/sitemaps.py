"""Карта сайта для поисковых систем (sitemap.xml)."""

from django.contrib.sitemaps import Sitemap
from django.db.models import Max
from django.urls import reverse

from .models import Category, Post

SITEMAP_DOMAIN = "clownix.ru"
SITEMAP_PROTOCOL = "https"


class StaticViewSitemap(Sitemap):
    """Главная страница."""

    domain = SITEMAP_DOMAIN
    protocol = SITEMAP_PROTOCOL
    changefreq = "daily"
    priority = 1.0

    def items(self):
        """Маршрут главной страницы."""
        return ["blog:home"]

    def location(self, item):
        """URL маршрута."""
        return reverse(item)


class CategorySitemap(Sitemap):
    """Страницы тем (разделов) каталога."""

    domain = SITEMAP_DOMAIN
    protocol = SITEMAP_PROTOCOL
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        """Все темы каталога."""
        return Category.objects.all()

    def lastmod(self, obj):
        """Дата последнего обновления опубликованной статьи темы."""
        return obj.posts.filter(status="published").aggregate(
            latest=Max("updated_at"),
        )["latest"]


class PostSitemap(Sitemap):
    """Опубликованные статьи."""

    domain = SITEMAP_DOMAIN
    protocol = SITEMAP_PROTOCOL
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        """Только опубликованные статьи."""
        return Post.objects.filter(status="published").select_related("category")

    def lastmod(self, obj):
        """Дата последнего обновления статьи."""
        return obj.updated_at
