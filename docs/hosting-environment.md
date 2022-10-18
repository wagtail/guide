# Hosting environment

The Wagtail Guide is a Dockerized Django application running on Heroku:

- Persistent data is stored in Heroku Postgres
- Heroku Data for Redis is used as a cache
- Logs are archived to Papertrail for historical analysis
- User-uploaded files are stored in AWS S3
- Email is handled by Mailgun
- Sentry is used for error monitoring

The application itself runs in Heroku's Europe region (`eu-west-1` (Dublin, Ireland)).

## Deployment

Deployment is handled automatically by Heroku. When commits are pushed to `main`, Heroku automatically begins building and deploying the site. This deployment only occurs _after_ CI has run and passed.

Currently, only a staging environment exists, so `main` deploys to staging. Once a production environment exists, this will be updated. 

## Access

The guide is hosted and managed by Torchbox's sysadmin team. Access is given only when needed following the [principle of least privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege). If you need access to Heroku, a project maintainer can contact Torchbox's sysadmin team who can provide access.

## Support

Whilst Torchbox's sysadmin team maintain and monitor the application's infrastructure, this does not imply [support](https://torchbox.com/wagtail-cms/hosting-application-support/).

## Useful links

- https://github.com/wagtail/guide/pull/47
