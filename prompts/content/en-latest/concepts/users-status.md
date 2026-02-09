# Users status

Page URL: https://guide.wagtail.org/en-latest/concepts/users-status/

> A Wagtail user can either be active or inactive. A user is active if they have the right permissions to log in and perform any action in the Admin interface.

A Wagtail user can either be active or inactive. A user is active if they have the right permissions to log in and perform any action in the [Admin interface](/en-latest/concepts/wagtail-interfaces/).

The status of a user determines whether that user still has the right permission to perform any action in the Admin interface. Wagtail provides for two statuses: active and inactive.

## Active status

A user is active if they have the right permission to log into the [Admin interface](/en-latest/concepts/wagtail-interfaces/) and perform an action. This action could be as simple as making a draft.

## Inactive status

When a user loses access to the [Admin interface](/en-latest/concepts/), they become inactive. Changing the status of a user from active to inactive is one of the rights reserved exclusively to an Administrator.

Making a user inactive is an alternative to deleting the user. This is because if you delete a user, you lose all the records or history of all actions that such a user has performed in the past. This might lead to some inconvenience. By making such users inactive instead, you deny them their access to the [Admin interface](/en-latest/concepts/wagtail-interfaces/) while preserving the records of their actions while they were active.
