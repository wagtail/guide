from wagtail import hooks


@hooks.register("register_rich_text_features")
def register_inline_code_feature(features):
    features.default_features.append("code")
