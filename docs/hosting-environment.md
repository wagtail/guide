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

Gunicorn, configured in [`gunicorn.conf.py`](../gunicorn.conf.py) and sized by `WEB_CONCURRENCY`. Can be overridden per app via a Config Var.

|        |                                                                           |
| ------ | ------------------------------------------------------------------------- |
| Server | Gunicorn `gthread`, `preload_app`                                         |
| Static | Whitenoise `CompressedManifestStaticFilesStorage`; `public/` at site root |
| User   | non-root `guide`                                                          |

### Dyno type and scale

One `basic` dyno, contrary to default infrastructure recommendations to use 2x `Standard-1x`. Key differences:

|                  | Basic                         | Standard-1x           |
| ---------------- | ----------------------------- | --------------------- |
| Cost             | $7/month                      | $25/month             |
| Web dynos        | 1 per process type            | Scalable horizontally |
| Metrics          | 24 hours, 10-minute intervals | Up to 7 days          |
| Threshold alerts | None                          | Error and performance |

## Maintenance mode

In special circumstances, use `heroku maintenance:on -a wagtail-guide-production` to serve a static 503 page and block access.

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

Heroku Postgres `standard-0` with daily overnight backups. Also used for search.

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

No `AWS_STORAGE_BUCKET_NAME` → local FS in the dyno (review apps / dev), lost on restart. Bucket versioning is set up in S3.

## Cache

Two databases on one Heroku Redis `mini` instance: `/0` default, `/1` renditions. Requires TLS, maxmemory: 25MB, `volatile-lru` eviction policy.

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

## AI providers

Both [`wagtail-ai`](https://github.com/wagtail/wagtail-ai) and `LLMTranslator` currently use [Scaleway Generative APIs](https://www.scaleway.com/en/generative-apis/).

## Scheduled tasks

Heroku Scheduler set up for:

| Job                         | Schedule         |
| --------------------------- | ---------------- |
| `update_index`              | Daily, overnight |
| `rebuild_references_index`  | Daily, overnight |
| `publish_scheduled`         | Every 10 minutes |
| `clearsessions`             | Daily, overnight |

## Operations checks

Only needed when changing hosting providers or setting up a new environment.

| Check                    | Command                                                   |
| ------------------------ | --------------------------------------------------------- |
| Database backup schedule | `heroku pg:backups:schedules -a wagtail-guide-production` |
| Log drain present        | `heroku addons -a wagtail-guide-production`               |
| Slack alerting routed    | Papertrail search → "Save & Setup an Alert"               |
| Media backed up          | S3 bucket Properties → versioning                         |
| Redis eviction policy    | `heroku redis:maxmemory -a wagtail-guide-production`      |

## Rollbacks

```bash
heroku releases --app wagtail-guide-production
heroku rollback --app wagtail-guide-production     # previous eligible release
heroku rollback v42 --app wagtail-guide-production # specific release
```

Reverts code, not migrations. See also [Releases](#releases) for what a deploy does to the database.

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

The `release` phase in [`heroku.yml`](../heroku.yml) runs `migrate` only. See [Rollbacks](#rollbacks) for what that means when a migration needs undoing.

### Continuous integration

GitHub Actions for all branch/PR quality assurance.

### Pre-production environments

No staging. Review Apps only.

## Access

Hosted and managed by Torchbox's sysadmin team, on [least privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege). Request Heroku access via a project maintainer.

Sysadmins also hold: Cloudflare, AWS (S3), Mailgun, Sentry, Scout, Papertrail/SolarWinds.

## Logs and monitoring

| Component                                                                            | Configuration                                                                                                                                                     |
| ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Application logs                                                                     | stdout → Heroku logplex → Papertrail (log drain)                                                                                                                  |
| Sentry                                                                               | On when `SENTRY_DSN` set, `DjangoIntegration`, `SENTRY_ENVIRONMENT=production`. Release from `HEROKU_RELEASE_VERSION` (requires the `runtime-dyno-metadata` lab). |
| Scout                                                                                | `scout_apm.django` first installed app. `SCOUT_MONITOR=false` for `release` and review apps.                                                                      |
| [DebugBear](https://www.debugbear.com/project/30072?share=7MSntGvPGbNE45exbh2iskTHv) | Web performance (Core Web Vitals, page weight). Public read-only dashboard, no credentials needed.                                                                |
| Heroku metrics                                                                       | Dyno CPU/memory, throughput/latency.                                                                                                                              |

Only Heroku's built-in metrics and the Papertrail drain are configured through this repository; everything else is set up and managed outside it, by Torchbox's sysadmin team.

### Application logs

Query Papertrail with the [SolarWinds Observability CLI](https://github.com/solarwinds/swo-cli).

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
| Retention       | Heroku: short-lived. Papertrail: 2 weeks live, archives on S3.            |
| Format          | `[timestamp][pid][level][logger] message`.                                |
| Notable loggers | `django.security` INFO; `mcp` WARNING (avoids per-request session noise). |
| Heroku router   | Filter on `router` for router lines, `status=5` for 5xx responses.        |

### Alerts

| Alert                                                               | Routed to             |
| ------------------------------------------------------------------- | --------------------- |
| [Checkly](https://www.checklyhq.com/) root-path monitor, production | Project Slack channel |

## Search

Wagtail search in Postgres (`wagtail.search.backends.database`, `wagtail.contrib.postgres`). No Elasticsearch/OpenSearch. Per-site; no separate public endpoint beyond the Wagtail API and search views.

## Support

Torchbox's sysadmin team maintain and monitor the infrastructure; this does not imply [support](https://torchbox.com/services/wagtail-cms/hosting-support/).
