from django.db import models

class Post(models.Model):
    """
    Модель постов для блога
    """

    STATUS_OPTIONS = (
        ("published", "Опубликованно"),
        ("draft", "Черновик"),
    )

    title = models.CharField(verbose_name="НАзвание поста", max_length=255)
    slug = models.SlugField(verbose_name="URL", max_length=255, blank=True)
    description = models.TextField(verbose_name="Краткое описание", max_length=500)
    text = models.TextField(verbose_name="Содержание поста")