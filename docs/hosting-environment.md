# Hosting environment

Dockerized Django application on Heroku, Europe region (`eu-west-1`, Dublin).

| Component | Service                                                                               |
| --------- | ------------------------------------------------------------------------------------- |
| Dyno      | 1 × `basic` web dyno, [`Dockerfile`](../Dockerfile) via [`heroku.yml`](../heroku.yml) |
| Database  | Heroku Postgres `standard-0` for production, `essential-0` otherwise                  |
| Cache     | Heroku Data for Redis `mini`                                                          |
| Logs      | Papertrail (via Heroku log drain)                                                     |
| Files     | AWS S3                                                                                |
| Email     | Mailgun SMTP                                                                          |
| Errors    | Sentry                                                                                |
| APM       | Scout                                                                                 |

See [MCP server](mcp.md) for `/mcp` operational requirements.

## Web process

Gunicorn, configured in [`gunicorn.conf.py`](../gunicorn.conf.py) and sized by `WEB_CONCURRENCY`.

|        |                                                                           |
| ------ | ------------------------------------------------------------------------- |
| Server | Gunicorn `gthread`, `preload_app`                                         |
| Static | Whitenoise `CompressedManifestStaticFilesStorage`; `public/` at site root |
| User   | non-root `guide`                                                          |

Concurrency values, worker recycling rates, and base image versions live in `gunicorn.conf.py` and `Dockerfile`.

## Container registry

No registry: Heroku's legacy Docker builder. Builds and stores the image itself, with no cross-environment image promotion. See [Deployment](#deployment).

## Environment variables

All config via Heroku Config Vars. No secrets in the repo. Defaults: [`settings/base.py`](../apps/guide/settings/base.py).

## SSL / TLS

Platform-managed (Heroku + Cloudflare). Django: `SECURE_SSL_REDIRECT`, `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`, HSTS enabled without `includeSubDomains`.

## Domains

| Domain                    | Serves     |
| ------------------------- | ---------- |
| `guide.wagtail.org`       | Site       |
| `guide-media.wagtail.org` | Media (S3) |

DNS and CDN: Cloudflare, managed by Torchbox sysadmins.

## Database

Heroku Postgres `standard-0` via `DATABASE_URL`, persistent connections (`conn_max_age`).

| Concern          | Detail                                                                   |
| ---------------- | ------------------------------------------------------------------------ |
| Search           | Postgres backend (`wagtail.search.backends.database`); no Elasticsearch. |
| Backups          | Heroku daily, retention per plan. **TODO** verify, and test restores.    |
| Restore to local | Below.                                                                   |

```bash
heroku pg:backups:download --output=./database_dumps/YYYYMMDD-wagtail-guide-production.dump --app wagtail-guide-production
dropdb --if-exists --host db.guide.orb.local --username=guide guide
createdb --host db.guide.orb.local --username=guide guide
psql -d guide -U guide --host db.guide.orb.local -c 'CREATE SCHEMA heroku_ext;'
pg_restore --clean --no-acl --if-exists --no-owner --host db.guide.orb.local --username=guide -d guide database_dumps/YYYYMMDD-wagtail-guide-production.dump
```

Adapt the hostname. `heroku_ext` must exist before restoring. Remote restores: not done, undocumented.

## File storage

AWS S3 via `django-storages` (`S3Boto3Storage`), `boto3` env credentials. Settings in `settings/base.py`:

| Setting                     | Effect                                                        |
| --------------------------- | ------------------------------------------------------------- |
| `AWS_QUERYSTRING_AUTH` off  | Unsigned URLs; public access via bucket policy.               |
| `AWS_DEFAULT_ACL` private   | Images public via bucket policy; documents served by Wagtail. |
| `AWS_S3_FILE_OVERWRITE` off | Wagtail guidance.                                             |
| `AWS_S3_CUSTOM_DOMAIN`      | Serves via `guide-media.wagtail.org`.                         |

No `AWS_STORAGE_BUCKET_NAME` → local FS in the dyno (review apps / dev), lost on restart. Bucket versioning, lifecycle, backups: unknown.

## Cache

Two databases on one Heroku Redis `mini` instance: `/0` default, `/1` renditions. `django-redis` with `IGNORE_EXCEPTIONS`; TLS cert validation disabled (self-signed). No `REDIS_URL` → database cache backend.

Not used for sessions or jobs — no Celery or worker process.

## CDN / Firewall

|        |                                                                                                                                                                                                                                                         |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CDN    | Cloudflare in front of the site.                                                                                                                                                                                                                        |
| Purge  | `wagtail.contrib.frontend_cache` (`CloudflareBackend`) on publish; enabled by `FRONTEND_CACHE_CLOUDFLARE_BEARER_TOKEN` or `..._TOKEN`.                                                                                                                  |
| Worker | [`cloudflare/caching-worker.js`](../cloudflare/caching-worker.js): skips private-cookie requests (`csrftoken`, `sessionid`), strips marketing params, caches a fixed set of status codes. A "Cache Everything" page rule would break the cookie bypass. |
| Media  | `guide-media.wagtail.org`, not purged by Wagtail.                                                                                                                                                                                                       |
| WAF    | Set up in Cloudflare, sysadmin-managed.                                                                                                                                                                                                                 |

## Email

Mailgun SMTP over TLS. Admin notifications and password resets only. No inbound handling.

## Error tracking and performance monitoring

| Component | Configuration                                                                                                                                                     |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sentry    | On when `SENTRY_DSN` set, `DjangoIntegration`, `SENTRY_ENVIRONMENT=production`. Release from `HEROKU_RELEASE_VERSION` (requires the `runtime-dyno-metadata` lab). |
| Scout     | `scout_apm.django` first installed app. `SCOUT_MONITOR=false` for `release` and review apps.                                                                      |
| Alerts    | None set up.                                                                                                                                                      |

## AI providers

Both [`wagtail-ai`](https://github.com/wagtail/wagtail-ai) and `LLMTranslator` currently use DeepSeek V4.1 Flash 1017 in [Scaleway Generative APIs](https://www.scaleway.com/en/generative-apis/).

## Scheduled tasks

Heroku scheduler set up for 3 jobs:

- `update_index`, daily overnight
- `publish_scheduled_pages`, every 10 minutes
- `clearsessions`, daily overnight

## Rollbacks

```bash
heroku releases --app wagtail-guide-production
heroku rollback --app wagtail-guide-production     # previous eligible release
heroku rollback v42 --app wagtail-guide-production # specific release
```

Reverts code, not migrations. **TODO** confirm supported procedure for releases with migrations.

## SSH access

```bash
heroku run -a wagtail-guide-production bash   # one-off dyno, not the web dyno
heroku ps:exec -a wagtail-guide-production    # inside a running dyno
```

## Deployment

Auto-deployed by Heroku on push to `main`, only after CI passes.

| Environment | Trigger           |
| ----------- | ----------------- |
| Production  | Commits to `main` |
| Review Apps | First-party PRs   |

### Releases

The `release` phase in [`heroku.yml`](../heroku.yml) runs `migrate` only.

### Continuous integration

GitHub Actions for all branch/PR quality assurance.

### Pre-production environments

No staging. Review Apps only.

## Access

Hosted and managed by Torchbox's sysadmin team, on [least privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege). Request Heroku access via a project maintainer.

Sysadmins also hold: Cloudflare, AWS (S3), Mailgun, Sentry, Scout, Papertrail/SolarWinds.

## Logs

### Application logs

stdout → Heroku logplex → Papertrail (log drain). Query with the [SolarWinds Observability CLI](https://github.com/solarwinds/swo-cli).

```bash
export SWO_API_TOKEN=...
export SWO_API_URL=https://api.na-01.cloud.solarwinds.com
```

```bash
swo logs get -s wagtail-guide-production --min-time '1 hour ago' error
swo logs get -s wagtail-guide-production --json | jq
swo logs get -s wagtail-guide-production -f
```

|                 |                                                                           |
| --------------- | ------------------------------------------------------------------------- |
| Retention       | Heroku: short-lived. Papertrail: per plan.                                |
| Format          | `[timestamp][pid][level][logger] message`.                                |
| Notable loggers | `django.security` INFO; `mcp` WARNING (avoids per-request session noise). |

### Heroku metrics

Heroku metrics dashboard: dyno CPU/memory, throughput/latency. No alerting.

## Search

Wagtail search in Postgres (`wagtail.search.backends.database`, `wagtail.contrib.postgres`). No Elasticsearch/OpenSearch. Per-site; no separate public endpoint beyond the Wagtail API and search views.

## Support

Torchbox's sysadmin team maintain and monitor the infrastructure; this does not imply [support](https://torchbox.com/services/wagtail-cms/hosting-support/).
