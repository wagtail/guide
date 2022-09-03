import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from wagtail.models import Page

from apps.core.models.feedback import Feedback


@csrf_exempt
def create_feedback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        page = Page.objects.filter(slug=data["slug"])[0]
        new_feedback = Feedback(
            feedback=data["feedback"],
            page=page,
            feedback_text=data["feedback_text"],
        )
        new_feedback.save()
    return HttpResponse(json.dumps(data))
