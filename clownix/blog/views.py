from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Post

SORT_OPTIONS = {
    "new": "-created_at",
    "old": "created_at",
}


def _apply_sort(qs, request):
    """Применить сортировку к QuerySet по GET-параметру ?sort=new|old."""
    sort = request.GET.get("sort", "new")
    order = SORT_OPTIONS.get(sort, "-created_at")
    return qs.order_by(order), sort


def home(request):
    """Главная страница со всеми опубликованными статьями."""
    qs = Post.objects.filter(status="published").select_related("category")
    qs, current_sort = _apply_sort(qs, request)
    return render(request, "blog/home.html", {
        "posts": qs,
        "current_sort": current_sort,
        "page_title": "Новые записи",
    })


def category_view(request, slug):
    """Страница темы: список опубликованных статей выбранной категории."""
    category = get_object_or_404(Category, slug=slug)
    qs = Post.objects.filter(
        status="published", category=category
    ).select_related("category")
    qs, current_sort = _apply_sort(qs, request)
    return render(request, "blog/category.html", {
        "posts": qs,
        "category": category,
        "current_sort": current_sort,
        "page_title": category.name,
    })


def post_detail(request, slug):
    """Детальная страница статьи с похожими записями той же темы."""
    post = get_object_or_404(
        Post.objects.select_related("category"),
        slug=slug,
        status="published",
    )
    related = (
        Post.objects.filter(status="published", category=post.category)
        .exclude(pk=post.pk)
        .order_by("-created_at")[:3]
    )
    return render(request, "blog/post_detail.html", {
        "post": post,
        "related": related,
        "page_title": post.title,
    })


def search(request):
    """Поиск статей по заголовку, описанию и полю команд."""
    q = (request.GET.get("q") or "").strip()
    posts = Post.objects.none()
    if q:
        posts = Post.objects.filter(
            status="published"
        ).filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(commands__icontains=q)
        ).select_related("category").order_by("-created_at")
    return render(request, "blog/search.html", {
        "posts": posts,
        "query": q,
        "page_title": f"Поиск: {q}" if q else "Поиск",
    })


def page_not_found(request, exception):
    """Кастомный 404 для любых несуществующих маршрутов."""
    return render(request, "blog/404.html", status=404)
