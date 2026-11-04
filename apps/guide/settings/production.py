from .base import *  # noqa: F403

# Allow enabling DEBUG (e.g. on review apps) via a `DEBUG` environment variable.
# Defaults to False for safety.
DEBUG = env.get("DEBUG", "false").lower() == "true"  # noqa: F405

SECRET_KEY = env["SECRET_KEY"]  # noqa: F405

# When DEBUG is enabled (e.g. on review apps), allow any host unless an
# explicit ALLOWED_HOSTS is provided. This avoids 400 errors on the app's
# dynamic hostname.
if allowed_hosts := env.get("ALLOWED_HOSTS"):  # noqa: F405
    ALLOWED_HOSTS = allowed_hosts.split(",")
elif DEBUG:
    ALLOWED_HOSTS = ["*"]

MANIFEST_LOADER["cache"] = True  # noqa: F405

# Force HTTPS redirect (enabled by default!)
# https://docs.djangoproject.com/en/stable/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = True

# This will allow the cache to swallow the fact that the website is behind TLS
# and inform the Django using "X-Forwarded-Proto" HTTP header.
# https://docs.djangoproject.com/en/stable/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# This is a setting activating the HSTS header. This will enforce the visitors to use
# HTTPS for an amount of time specified in the header. Since we are expecting our apps
# to run via TLS by default, this header is activated by default.
# The header can be deactivated by setting this setting to 0, as it is done in the
# dev and testing settings.
# https://docs.djangoproject.com/en/stable/ref/settings/#secure-hsts-seconds
DEFAULT_HSTS_SECONDS = 30 * 24 * 60 * 60  # 30 days
SECURE_HSTS_SECONDS = int(
    env.get("SECURE_HSTS_SECONDS", DEFAULT_HSTS_SECONDS)  # noqa: F405
)

# Do not use the `includeSubDomains` directive for HSTS. This needs to be prevented
# because the apps are running on client domains (or our own for staging), that are
# being used for other applications as well. We should therefore not impose any
# restrictions on these unrelated applications.
# https://docs.djangoproject.com/en/3.2/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = False

# https://docs.djangoproject.com/en/stable/ref/settings/#secure-content-type-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True

# Content Security Policy
#
# The policy is defined in `base.py`. The report URI is environment-specific,
# and must be quoted as a list. https://docs.djangoproject.com/en/6.0/ref/middleware/#django.middleware.csp.ContentSecurityPolicyMiddleware
SECURE_CSP["report-uri"] = [  # noqa: F405
    "https://o4504043711037440.ingest.us.sentry.io/api/4504043711037440/security/?sentry_key=8660a4ef016e4bda918d7b1fe943daa3"
]

# Referrer-policy header settings.
# https://django-referrer-policy.readthedocs.io/en/1.0/

REFERRER_POLICY = env.get(  # noqa: F405
    "SECURE_REFERRER_POLICY", "no-referrer-when-downgrade"
).strip()

# Allow the redirect importer to work in load-balanced / cloud environments.
# https://docs.wagtail.io/en/v2.13/reference/settings.html#redirects
WAGTAIL_REDIRECTS_FILE_STORAGE = "cache"
