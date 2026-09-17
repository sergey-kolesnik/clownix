from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Тема (раздел) каталога Linux-команд. Используется для группировки статей."""
    name = models.CharField("Название темы", max_length=120)
    slug = models.SlugField("URL", max_length=140, unique=True, blank=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        ordering = ("order", "name")

    def save(self, *args, **kwargs):
        """Автоматически сгенерировать slug из названия, если он пуст."""
        if not self.slug:
            self.slug = slugify(self.name)[:140] or "topic"
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """URL страницы со списком статей темы."""
        return reverse("blog:category", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        """Строковое представление — название темы."""
        return self.name


def post_upload_path(instance, filename):
    """Путь сохранения файла обложки статьи в MEDIA_ROOT."""
    return f"posts/covers/{filename}"


def inline_image_upload_path(instance, filename):
    """Путь сохранения inline-картинки, встраиваемой в текст статьи."""
    return f"posts/inline/{filename}"


class Post(models.Model):
    """Статья-справочник по Linux-командам с обложкой, описанием и телом."""
    STATUS_CHOICES = (
        ("published", "Опубликовано"),
        ("draft", "Черновик"),
    )

    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("URL", max_length=255, unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="posts",
        verbose_name="Тема",
    )
    cover = models.ImageField(
        "Картинка-обложка (превью и заголовок)",
        upload_to=post_upload_path,
    )
    description = models.TextField("Краткое описание", max_length=500)
    commands = models.TextField(
        "Команды",
        help_text="Будут отображены в блоке <pre class='cmd'>. "
                  "Разделяйте блоки строкой из ---",
        blank=True,
    )
    body = models.TextField(
        "Текст статьи",
        help_text="Поддерживается перенос строк и вставка картинок. "
                  "Чтобы вставить картинку — загрузите её ниже и "
                  "вставьте плейсхолдер [[img:ID]] в нужное место.",
        blank=True,
    )
    status = models.CharField(
        "Статус", max_length=10, choices=STATUS_CHOICES, default="published",
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        """Сгенерировать уникальный slug из заголовка, если он пуст или занят."""
        if not self.slug:
            base = slugify(self.title)[:240] or "post"
            slug = base
            i = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """URL страницы детального просмотра статьи."""
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        """Строковое представление — заголовок статьи."""
        return self.title


class PostImage(models.Model):
    """Inline-картинка, встраиваемая в тело статьи через плейсхолдер [[img:ID]]."""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="images",
        verbose_name="Статья",
    )
    image = models.ImageField("Картинка", upload_to=inline_image_upload_path)
    caption = models.CharField("Подпись", max_length=255, blank=True)

    class Meta:
        verbose_name = "Картинка в статье"
        verbose_name_plural = "Картинки в статье"

    def placeholder(self) -> str:
        """Плейсхолдер [[img:ID]] для вставки картинки в тело статьи."""
        return f"[[img:{self.id}]]"

    def __str__(self) -> str:
        """Строковое представление для админки: ID и заголовок статьи."""
        return f"Image #{self.id} for {self.post.title}"


class Command(models.Model):
    """Структурированная команда с описанием для статьи."""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="commands_list",
        verbose_name="Статья",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    code = models.TextField(
        "Команда",
        help_text="Можно несколько строк, переносы сохранятся.",
    )
    description = models.TextField(
        "Описание",
        help_text="Что делает команда, зачем, какие нюансы.",
        blank=True,
    )

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды (с описанием)"
        ordering = ("order", "id")

    def __str__(self) -> str:
        """Строковое представление — первая строка команды и заголовок статьи."""
        first_line = (self.code or "").splitlines()[0][:40] if self.code else ""
        return f"{first_line} — {self.post.title}"
