import factory
from factory.django import DjangoModelFactory
from wagtail.documents import get_document_model
from wagtail.images import get_image_model_string


class ImageFactory(DjangoModelFactory):
    title = "Blue"
    file = factory.django.ImageField(color="blue", width=300, height=300)

    class Meta:
        model = get_image_model_string()
        django_get_or_create = ("title",)


class DocumentFactory(DjangoModelFactory):
    title = factory.Faker("bs")
    file = factory.django.FileField()

    class Meta:
        model = get_document_model()
        django_get_or_create = ("title",)
