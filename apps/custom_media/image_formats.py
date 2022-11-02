from wagtail.images.formats import get_image_format

fullwidth = get_image_format("fullwidth")
fullwidth.filter_spec = "width-900"
