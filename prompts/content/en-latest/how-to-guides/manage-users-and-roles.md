# Manage users and roles

Page URL: https://guide.wagtail.org/en-latest/how-to-guides/manage-users-and-roles/

> As an administrator, a common task will be adding, modifying or removing user profiles.

Wagtail allows several users to manage content in the admin interface. These users have roles, which determine the access rights they can exercise.

Note: The user roles in your [Admin interface](/en-latest/concepts/wagtail-interfaces/) may be different from these because Wagtail is highly customizable. If this is the case, contact your web developer for more details.

By default, there are three user roles:

## Administrator

An administrator has the highest level of access to the admin interface, and are able to perform all actions in the [Admin interface](/en-latest/concepts/wagtail-interfaces/). A common task of an administrator is to add, modify, or remove user profiles. As an administrator, you can add, modify, and remove users via the Users interface. To access the Users interface, go to **Settings > Users** from the Wagtail [Sidebar](/en-latest/how-to-guides/find-your-way-around/).

In the [Users interface](/en-latest/concepts/wagtail-interfaces/), you can see all of your users, their usernames, roles, and status. The status of a user can either be active or inactive. You can sort this listing either by Name or Username.

![The users listing with search and a CTA to add users This shows three rows with users Olivia Ava Admin User and Muddy Waters](https://guide-media.wagtail.org/images/The_users_listing_with_search_and_a_CTA_to_add.width-900_HrsMly9.png)

Select multiple users by checking the checkbox to the left of each user row, then use the bulk action bar at the bottom to perform an action on all selected users.

![The users listing with checkboxes in the first column The checkbox for the Admin user row has been checked and a footer with different actions shows at the bottom of the screen](https://guide-media.wagtail.org/images/The_users_listing_with_checkboxes_in_the_first.width-900_j4UH2pO.png)

Clicking on a user’s name opens their profile in an [edit screen.](/en-latest/concepts/wagtail-interfaces/) From here, you can then edit that user's details. It is also possible to change users’ passwords from their edit screen, but it is worth encouraging your users to use the **Forgotten password** link on the login screen instead. This should save you some time!

## Moderator

A moderator has the next level of access after an administrator. A moderator has access to creating drafts and publishing them. However, a moderator can't access the [Settings](/en-latest/how-to-guides/find-your-way-around/) section of the [Admin interface](/en-latest/concepts/wagtail-interfaces/).

## Editor

An editor has the least level of access to the [Admin interface](/en-latest/concepts/wagtail-interfaces/). An editor can only create drafts but not publish them. Also, as in the case of a moderator, an editor can't access the [Settings](/en-latest/how-to-guides/find-your-way-around/) section of the [Admin interface](/en-latest/concepts/wagtail-interfaces/).
