---
title: 'Manage API tokens'
description: 'API tokens let applications and integrations connect to the Wagtail API on behalf of a user account. Learn how to create, rename, and revoke them.'
last_modified: '2026-11-10'
---

# Manage API tokens

Page URL: https://guide.wagtail.org/en/how-to-guides/manage-api-tokens/

> API tokens let applications and integrations connect to the Wagtail API on behalf of a user account. Learn how to create, rename, and revoke them.

API tokens let applications and integrations connect to the [Wagtail API](/en/concepts/wagtail-api/) on behalf of a user account. You can create, rename, and revoke tokens from the [Admin interface](/en/concepts/wagtail-interfaces/).

API tokens are only available when developers have enabled the Wagtail API on your site. It's also possible that the token management features in your Admin interface are different from the default features. This is because Wagtail is highly customizable. If this is the case, contact your web developer for more information.

## About API tokens

An API token is a secret key that an integration sends with each request to the API. Each token belongs to a user account, and the integration acts as that user, with exactly the same permissions as the user has in the Admin interface.

A few things to know about tokens:

- **A token is only shown once.** Wagtail only stores a scrambled version of each token, so nobody can view it again after creation, not even administrators.
- **Tokens start with `wagtail_`.** This makes it easier for security tools to detect a token that's been shared by mistake, for example in a public code repository.
- **Revoking is immediate.** Once you revoke a token, the API stops accepting it for anything other than public content.

Warning: Treat API tokens like passwords. Anyone who has a token can read and change content with the permissions of the user it belongs to.

### Use dedicated accounts for integrations

Consider creating a dedicated user account for each integration rather than using someone's personal account. You can give that account only the permissions the integration needs, for example editing pages in a single section of the site. This also means you can revoke the integration's access without affecting a real person's account, and the [page history](/en/how-to-guides/manage-pages/) clearly shows which changes were made by the integration.

To learn how to set up users and their permissions, see [Manage users and roles](/en/how-to-guides/manage-users-and-roles/).

## View API tokens

Go to **Settings > API tokens** from the [Sidebar](/en/how-to-guides/find-your-way-around/) to see the tokens you can manage. The listing shows the following columns for each token:

- **Token**: the first few characters of the token, to help you recognize it.
- **Name**: the label given to the token when it was created.
- **User**: the user account the token belongs to.
- **Created**: when the token was created.
- **Last used**: when an integration last used the token.
- **Revoked**: when the token was revoked, if it has been.

<!-- TODO: screenshot - suggested alt: "API tokens listing showing three tokens with their token prefix, name, user, created date, last used date, and revoked date columns, with the filters panel open to the right showing User, Created, Last used, and Revoked filters" -->

You can filter the listing by user, by creation date, by last used date, and by whether tokens are revoked. The **Last used** filter is useful to find tokens that haven't been used in a while and may no longer be needed.

Note that the last used date is updated periodically rather than on every request, so it may be slightly behind.

## Create an API token

To create an API token:

1. Go to **Settings > API tokens** from the [Sidebar](/en/how-to-guides/find-your-way-around/).
2. Click **Add API token**.
3. Enter a **Name** that describes what the token is for, such as the name of the integration that will use it.
4. Select the **User** the token will belong to. The list only shows the users you're allowed to create tokens for.
5. Click **Create**.
6. Click **Copy token** to copy the token to your clipboard, and store it somewhere safe, such as a password manager, or share it securely with the person setting up the integration.

<!-- TODO: screenshot - suggested alt: "API token created screen with a message saying the token has been created and will never be shown again, a read-only field containing the full token starting with wagtail_, and Copy token and Back to API tokens buttons" -->

Make sure you copy the token before leaving this screen. It will never be shown again. If you lose it, revoke it and create a new one.

Congratulations! Your integration can now connect to the API with this token.

## Rename an API token

To rename a token, go to **Settings > API tokens** and click the token you want to rename. Change its **Name**, then click **Save**. You can't change the user a token belongs to, or the token itself.

The status side panel on this screen shows whether the token is _Active_ or _Revoked_, and when it was last used.

## Revoke an API token

Revoke a token when an integration no longer needs access, when a token may have been shared with the wrong people, or when the person responsible for an integration leaves your organization.

To revoke a token:

1. Go to **Settings > API tokens** from the [Sidebar](/en/how-to-guides/find-your-way-around/).
2. Click the **More options** (three dots) icon next to the token, then click **Revoke**. Alternatively, click the token to open it and click **Revoke** from the edit screen.
3. Click **Yes, revoke** to confirm.

Revoking can't be undone. If an integration needs access again, create a new token for it. Revoked tokens stay in the listing with the date they were revoked, so you keep a record of past access.

## Permissions for managing tokens

Administrators can give users the permission to manage API tokens through groups, from **Settings > Groups**. The _API token_ permissions let users add, change, and delete (revoke) tokens:

- Users with these permissions can manage tokens that belong to their own account.
- To manage tokens for other users, they also need the permission to change users. Keep in mind that this permission also gives access to sensitive account features, such as resetting passwords and changing group membership.
- Tokens that belong to administrators can only be managed by other administrators.

The creation and revocation of every token is recorded in the [Site history report](/en/concepts/reports/), so you can check who created or revoked a token and when.
