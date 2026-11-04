from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment, select_autoescape


def environment(**options):
    # Django's Jinja2 backend escapes every template for HTML by default.
    # Markdown and plain text templates must output text as is, so that
    # agents get `'` and `&` rather than `&#39;` and `&amp;`.
    options["autoescape"] = select_autoescape(
        disabled_extensions=("md.jinja", "txt.jinja"),
        default_for_string=True,
        default=True,
    )
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
        }
    )
    return env
