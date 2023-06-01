import json

from django.conf import settings
from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory
from apps.core.models.feedback import Feedback


class TestFeedback(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.target_page = ContentPageFactory(parent=self.home)

    def test_happy_feedback(self):
        payload = {
            "feedback": "happy",
        }
        res = self.client.post(
            self.target_page.url,
            json.dumps(payload),
            content_type="application/json; charset=UTF-8",
        )
        data = json.loads(res.content)
        feedback_obj = Feedback.objects.get(pk=data["pk"])
        self.assertEqual(feedback_obj.feedback, "happy")
        self.assertEqual(feedback_obj.feedback_text, "")
        self.assertEqual(feedback_obj.page.specific, self.target_page)

    def test_unhappy_feedback(self):
        payload = {
            "feedback": "unhappy",
        }
        res = self.client.post(
            self.target_page.url,
            json.dumps(payload),
            content_type="application/json; charset=UTF-8",
        )
        data = json.loads(res.content)
        feedback_obj = Feedback.objects.get(pk=data["pk"])
        self.assertEqual(feedback_obj.feedback, "unhappy")
        self.assertEqual(feedback_obj.feedback_text, "")
        self.assertEqual(feedback_obj.page.specific, self.target_page)

    def test_update_feedback_unhappy(self):
        payload1 = {
            "feedback": "unhappy",
        }
        res1 = self.client.post(
            self.target_page.url,
            json.dumps(payload1),
            content_type="application/json; charset=UTF-8",
        )
        data1 = json.loads(res1.content)
        payload2 = {"pk": data1["pk"], "feedback_text": "some unhappy feedback text"}
        res2 = self.client.post(
            self.target_page.url,
            json.dumps(payload2),
            content_type="application/json; charset=UTF-8",
        )
        data2 = json.loads(res2.content)
        self.assertEqual(data1["pk"], data2["pk"])
        feedback_obj = Feedback.objects.get(pk=data1["pk"])
        self.assertEqual(feedback_obj.feedback_text, "some unhappy feedback text")
        self.assertEqual(feedback_obj.feedback, "unhappy")
        self.assertEqual(feedback_obj.page.specific, self.target_page)

    def test_update_feedback_happy(self):
        payload1 = {
            "feedback": "happy",
        }
        res1 = self.client.post(
            self.target_page.url,
            json.dumps(payload1),
            content_type="application/json; charset=UTF-8",
        )
        data1 = json.loads(res1.content)
        payload2 = {"pk": data1["pk"], "feedback_text": "some happy feedback text"}
        res2 = self.client.post(
            self.target_page.url,
            json.dumps(payload2),
            content_type="application/json; charset=UTF-8",
        )
        data2 = json.loads(res2.content)
        self.assertEqual(data1["pk"], data2["pk"])
        feedback_obj = Feedback.objects.get(pk=data1["pk"])
        self.assertEqual(feedback_obj.feedback_text, "some happy feedback text")
        self.assertEqual(feedback_obj.feedback, "happy")
        self.assertEqual(feedback_obj.page.specific, self.target_page)

    def test_csrf_token_exists(self):
        cookie = self.client.cookies.get(settings.CSRF_COOKIE_NAME)
        self.assertIsNone(cookie)

        # After opening a page, a cookie containing the CSRF token must be set,
        # as it is used in the JS when submitting feedback.
        self.client.get(self.target_page.url)
        cookie = self.client.cookies.get(settings.CSRF_COOKIE_NAME)
        self.assertIsNotNone(cookie)
