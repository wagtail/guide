# Scheduled publishing

Page URL: https://guide.wagtail.org/en-latest/concepts/scheduled-publishing/

Wagtail supports scheduling content for new and existing pages, as well as when configured for [snippets](/en-latest/how-to-guides/manage-snippets/). Page publishing can be scheduled through the _Set schedule_ feature in the _Status_ side panel of the _Edit_ page (see [Manage pages](/en-latest/how-to-guides/manage-pages/)).

## Scheduling content updates

The basic workflow is as follows:

-   Scheduling is done by setting the _go-live at_ field of the page and clicking _Publish_.
-   Scheduling a revision for a page that is not currently live means that page will go live when the scheduled time comes.
-   Scheduling a new version for a page that is already live means that the new version will be published when the time comes.
-   If the page has a scheduled revision and you set another revision to publish immediately (i.e. clicking _Publish_ with the _go-live at_ field unset), the scheduled revision will be unscheduled.
-   If the page has a scheduled revision and you schedule another revision to publish (i.e. clicking _Publish_ with the _go-live at_ field set), the existing scheduled revision will be unscheduled and the new revision will be scheduled instead.

Note that you have to click _Publish_ after setting the _go-live at_ field for the revision to be scheduled. Saving a draft revision with the _go-live at_ field without clicking _Publish_ will not schedule it to be published.

The _History_ view for a given page will show which revision is scheduled and when it is scheduled. A scheduled revision in the list will also provide an _Unschedule_ button to cancel it.

## Scheduled unpublishing

In addition to scheduling a page to be published, it is also possible to schedule a page to be unpublished by setting the _expire at_ field. However, unlike with publishing, the unpublishing schedule is applied to the live page instance rather than a specific revision. This means that any change to the _expire at_ field will only be effective once the associated revision is published (i.e. when the changes are applied to the live instance). To illustrate:

-   Scheduled unpublishing is done by setting the _expire at_ field of the page and clicking _Publish_. If the _go-live at_ field is also set, then the unpublishing schedule will only be applied after the revision goes live.
-   Consider a live page that is scheduled to be unpublished on e.g. 14 June. Then sometime before the schedule, consider that a new revision is scheduled to be published on a date that’s **earlier** than the unpublishing schedule, e.g. 9 June. When the new revision goes live on 9 June, the _expire at_ field contained in the new revision will replace the existing unpublishing schedule. This means:
    -   If the new revision contains a different _expire at_ field (e.g. 17 June), the new revision will go live on 9 June and the page will not be unpublished on 14 June but will be unpublished on 17 June.
    -   If the new revision has the _expire at_ field unset, the new revision will go live on 9 June and the unpublishing schedule will be unset, thus the page will not be unpublished.
-   Consider another live page that is scheduled to be unpublished on e.g. 14 June. Then sometime before the schedule, consider that a new revision is scheduled to be published on a date that’s **later** than the unpublishing schedule, e.g. 21 June. The new revision will not take effect until it goes live on 21 June, so the page will still be unpublished on 14 June. This means:
    -   If the new revision contains a different _expire at_ field (e.g. 25 June), the page will be unpublished on 14 June, the new revision will go live on 21 June and the page will be unpublished again on 25 June.
    -   If the new revision has the _expire at_ field unset, the page will be unpublished on 14 June and the new revision will go live on 21 June.

Once a page expires, its [page status](/en-latest/concepts/page-status/) in the CMS changes to "Expired".

## Scheduling frequency

For scheduling to work, developers must have set up the [publish_scheduled](https://docs.wagtail.org/en/stable/reference/management_commands.html#publish-scheduled) management command. This can be run every hour, or every 15 minutes, or at any other interval depending on the needs of the website.
