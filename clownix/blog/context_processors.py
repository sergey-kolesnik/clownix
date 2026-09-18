from .models import Category

PROJECT_VERSION = "2.0.2"


def sidebar_context(request):
    """Прокинуть список всех тем и версию проекта в каждый шаблон."""
    return {
        "sidebar_categories": Category.objects.all(),
        "PROJECT_VERSION": PROJECT_VERSION,
    }
