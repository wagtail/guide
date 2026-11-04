"""
Check the agent readiness eval's test cases, without calling a model.

For every case in `tests.yaml`, this runs the text checks (not the
`llm-rubric`, which needs a model) against:

- the case's `reference` answer, which must pass;
- answers that a sound case must reject: an empty reply, a refusal, a reply
  with only the expected URLs, and the reference with its URLs removed.

It also flags prompts that contain the facts their checks look for, as those
checks would pass whatever the answer says.

A failure means the case or its checks need fixing before the eval's scores
for that case can be trusted.
"""

import re
import sys
from pathlib import Path

import yaml

TESTS = Path(__file__).resolve().parent.parent / "tests.yaml"
TEXT_CHECKS = {"icontains", "icontains-any", "icontains-all", "regex", "not-regex"}
# Matches URL checks, whether plain text or regex (with escaped dots).
URL_FRAGMENT = re.compile(r"(guide|docs)\\?\.wagtail\\?\.org")
URL_PATTERN = re.compile(r"https?://\S+")


def values(assertion):
    value = assertion["value"]
    return value if isinstance(value, list) else [value]


def passes(assertion, answer):
    kind = assertion["type"]
    text = answer.lower()
    if kind == "icontains":
        return values(assertion)[0].lower() in text
    if kind == "icontains-any":
        return any(value.lower() in text for value in values(assertion))
    if kind == "icontains-all":
        return all(value.lower() in text for value in values(assertion))
    if kind == "regex":
        return re.search(assertion["value"], answer) is not None
    if kind == "not-regex":
        return re.search(assertion["value"], answer) is None
    raise ValueError(kind)


def passes_all(checks, answer):
    return all(passes(assertion, answer) for assertion in checks)


def sample_url(value, kind):
    """A URL that a URL check accepts, from its text or regex."""
    if kind != "regex":
        return value
    value = value.replace(r"(-[\w.]+)?", "")
    value = re.sub(r"\(([^|)]*)(\|[^)]*)?\)", r"\1", value)
    return value.replace("\\", "")


def null_answers(checks, reference):
    urls = [
        sample_url(value, assertion["type"])
        for assertion in checks
        for value in values(assertion)
        if URL_FRAGMENT.search(value)
    ]
    return {
        "empty": "",
        "refusal": "I don't know.",
        "URLs only": " ".join(f"https://{url}/" for url in urls),
        "no URLs": URL_PATTERN.sub("", reference),
    }


def leaks(checks, prompt):
    """Fact values that already appear in the prompt."""
    prompt = prompt.lower()
    found = []
    for assertion in checks:
        facts = [v for v in values(assertion) if not URL_FRAGMENT.search(v)]
        leaked = [v for v in facts if v.lower() in prompt]
        # Leaks matter when they make a check pass on their own.
        if assertion["type"] == "icontains-all":
            if facts and len(leaked) == len(facts):
                found += leaked
        else:
            found += leaked
    return found


def check():
    problems = []
    for case in yaml.safe_load(TESTS.read_text()):
        name = case["description"]
        checks = [a for a in case["assert"] if a["type"] in TEXT_CHECKS]
        reference = case["vars"]["reference"]
        if not checks:
            problems.append(f"{name}: no text checks")
            continue
        # Versioned guide URLs redirect to the current page, so they count too.
        versioned = reference.replace(
            "guide.wagtail.org/en/", "guide.wagtail.org/en-6.3.x/"
        )
        for assertion in checks:
            if not passes(assertion, reference):
                problems.append(f"{name}: reference fails {assertion}")
            if not passes(assertion, versioned):
                problems.append(f"{name}: versioned reference fails {assertion}")
        for label, answer in null_answers(checks, reference).items():
            if passes_all(checks, answer):
                problems.append(f"{name}: {label} answer passes")
        if leaked := leaks(checks, case["vars"]["prompt"]):
            problems.append(f"{name}: prompt contains checked facts {leaked}")
        if not any(a["type"] == "llm-rubric" for a in case["assert"]):
            problems.append(f"{name}: no llm-rubric")
    return problems


def main():
    problems = check()
    for problem in problems:
        print(problem)
    cases = len(yaml.safe_load(TESTS.read_text()))
    print(f"{cases} cases, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
