from wagtail.models import Page

class HomePage(Page):
    subpage_types = ['content.ContentPage']
    max_count = 1
