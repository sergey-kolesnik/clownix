from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Post, PostImage, Command


class PostImageInline(admin.TabularInline):
    """Inline-форма для загрузки картинок, встраиваемых в тело статьи."""
    model = PostImage
    extra = 1
    fields = ("image", "caption", "preview", "insert")
    readonly_fields = ("preview", "insert")

    def preview(self, obj):
        """Превью загруженной картинки прямо в форме админки."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:80px;border-radius:6px" />',
                obj.image.url,
            )
        return "—"

    def insert(self, obj):
        """Кнопка вставки плейсхолдера [[img:ID]] в поле body."""
        if obj.pk:
            return format_html(
                '<button type="button" class="button insert-img-btn" '
                'data-placeholder="[[img:{}]]">Вставить в текст</button>',
                obj.pk,
            )
        return "Сначала сохраните"
    insert.short_description = "Вставка"


class CommandInline(admin.StackedInline):
    """Inline-форма структурированных пар «команда — описание» в статье."""
    model = Command
    extra = 1
    fields = ("order", "code", "description")
    ordering = ("order", "id")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для тем каталога."""
    list_display = ("name", "slug", "order", "post_count")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def post_count(self, obj):
        """Количество статей в теме для отображения в списке."""
        return obj.posts.count()
    post_count.short_description = "Статей"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админка для статей-справочников."""
    list_display = ("title", "category", "status", "created_at", "cover_thumb")
    list_filter = ("category", "status", "created_at")
    search_fields = ("title", "description", "commands", "body")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("cover_preview", "created_at", "updated_at")
    list_editable = ("status",)
    inlines = [CommandInline, PostImageInline]
    date_hierarchy = "created_at"
    save_on_top = True

    fieldsets = (
        ("Основное", {
            "fields": ("title", "slug", "category", "status"),
        }),
        ("Обложка", {
            "fields": ("cover", "cover_preview"),
            "description": "Эта же картинка отображается в превью карточки.",
        }),
        ("Контент", {
            "fields": ("description", "commands", "body"),
        }),
        ("Служебное", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def cover_preview(self, obj):
        """Крупное превью обложки в форме редактирования статьи."""
        if obj.cover:
            return format_html(
                '<img src="{}" style="max-height:160px;border-radius:8px" />',
                obj.cover.url,
            )
        return "Загрузите картинку"
    cover_preview.short_description = "Превью обложки"

    def cover_thumb(self, obj):
        """Маленькое превью обложки в списке статей админки."""
        if obj.cover:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:4px" />',
                obj.cover.url,
            )
        return "—"
    cover_thumb.short_description = "Превью"

    class Media:
        """Подключить JS для кнопки «Вставить в текст» в PostImageInline."""
        js = ("blog/admin_insert_image.js",)


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    """Отдельная админка для структурированных команд (вдобавок к inline)."""
    list_display = ("post", "order", "code_preview")
    list_filter = ("post",)
    search_fields = ("code", "description", "post__title")
    list_editable = ("order",)
    autocomplete_fields = ("post",)

    def code_preview(self, obj):
        """Краткий однострочный анонс команды для списка."""
        text = (obj.code or "").replace("\n", " ⏎ ")
        return text[:80]
    code_preview.short_description = "Команда"
