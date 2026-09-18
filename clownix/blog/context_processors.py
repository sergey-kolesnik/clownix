from .models import Category


def sidebar_context(request):
    """Прокинуть список всех тем в каждый шаблон для отрисовки сайдбара."""
    return {
        "sidebar_categories": Category.objects.all(),
    }
