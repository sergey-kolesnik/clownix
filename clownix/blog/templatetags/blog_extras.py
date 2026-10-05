"""Кастомные шаблонные фильтры и теги для приложения blog."""

import re
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from ..models import PostImage

register = template.Library()


@register.filter(name="command_blocks")
def command_blocks(value: str) -> str:
    """Разбить текст поля commands на блоки <pre class='cmd'> по разделителю '---'."""
    if not value:
        return ""
    blocks = [b.strip("\n").rstrip() for b in value.split("\n---\n")]
    html = "".join(
        f'<pre class="cmd">{b}</pre>' for b in blocks if b.strip()
    )
    return mark_safe(html)


_IMG_RE = re.compile(r"\[\[img:(\d+)\]\]")
_IMG_PARAGRAPH_RE = re.compile(
    r"<p>\s*\[\[img:(\d+)\]\]\s*</p>", re.IGNORECASE
)
_HTML_TAG_RE = re.compile(r"<(?:p|h[1-6]|ul|ol|li|figure|img|a|blockquote|div|table|pre)\b", re.IGNORECASE)


@register.filter(name="inline_images")
def inline_images(value: str) -> str:
    """Заменить плейсхолдеры [[img:ID]] на <figure> и сверстать абзацы.

    Тело статьи может быть двух видов:
    - HTML из WYSIWYG-редактора (CKEditor) — отдаётся как есть;
    - старый простой текст — оборачивается в абзацы <p> как раньше.
    """
    if not value:
        return ""

    ids = {
        int(m)
        for m in set(_IMG_RE.findall(value)) | set(_IMG_PARAGRAPH_RE.findall(value))
    }
    images = {img.pk: img for img in PostImage.objects.filter(pk__in=ids)}

    def figure_html(image_id):
        """HTML-блок <figure> для inline-картинки по её ID."""
        img = images.get(int(image_id))
        if img is None:
            return ""
        caption = (
            f"<figcaption>{escape(img.caption)}</figcaption>" if img.caption else ""
        )
        alt = escape(img.caption or "")
        return (
            f'<figure class="article-figure">'
            f'<img src="{img.image.url}" alt="{alt}" />'
            f"{caption}</figure>"
        )

    # Плейсхолдер, занявший целый абзац (CKEditor оборачивает его в <p>),
    # заменяем вместе с абзацем, чтобы не получать <figure> внутри <p>.
    rendered = _IMG_PARAGRAPH_RE.sub(
        lambda m: figure_html(m.group(1)), value
    )
    # Оставшиеся плейсхолдеры заменяем на месте.
    rendered = _IMG_RE.sub(lambda m: figure_html(m.group(1)), rendered)

    if _HTML_TAG_RE.search(rendered):
        # Контент уже HTML из редактора — отдаём без дополнительной обёртки.
        return mark_safe(rendered)

    paragraphs = []
    for paragraph in rendered.split("\n\n"):
        p = paragraph.strip()
        if not p:
            continue
        paragraphs.append(f"<p>{p.replace(chr(10), '<br>')}</p>")
    return mark_safe("".join(paragraphs))
