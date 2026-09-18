"""Кастомные шаблонные фильтры и теги для приложения blog."""

import re
from django import template
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


@register.filter(name="inline_images")
def inline_images(value: str) -> str:
    """Заменить плейсхолдеры [[img:ID]] на <figure> и сверстать абзацы."""
    if not value:
        return ""

    def repl(match):
        """Подставить inline-картинку по её ID; вернуть пустую строку, если нет."""
        try:
            img = PostImage.objects.get(pk=int(match.group(1)))
        except PostImage.DoesNotExist:
            return ""
        caption = (
            f"<figcaption>{img.caption}</figcaption>" if img.caption else ""
        )
        return (
            f'<figure class="article-figure">'
            f'<img src="{img.image.url}" alt="{img.caption}" />'
            f"{caption}</figure>"
        )

    rendered = _IMG_RE.sub(repl, value)

    paragraphs = []
    for paragraph in rendered.split("\n\n"):
        p = paragraph.strip()
        if not p:
            continue
        paragraphs.append(f"<p>{p.replace(chr(10), '<br>')}</p>")
    return mark_safe("".join(paragraphs))
