from pathlib import Path
import os


def get_transform(vars, context):
    file_path = Path(__file__).resolve().parent / vars["page"].replace("file://", "")
    with open(file_path) as file:
        page = file.read()

    before, after = page.split(
        vars["image"].replace("{{ image_url }}", vars["image_url"])
    )

    return {
        **vars,
        "form_context_before": before,
        "forms_context_after": after,
    }
