# Manage snippets

Page URL: https://guide.wagtail.org/en-latest/how-to-guides/manage-snippets/

> Snippets allow you to create elements on a website once and reuse them in multiple places.

## The use of snippets

Snippets allow you to create elements on a website once and reuse them in multiple places. You only have to change something in a snippet once, and the changes appear in all occurrences.

The use of snippets varies between websites. Wagtail developers use snippets for the following purposes:

-   For blog post authors. As a result, you can add them to multiple pages and manage them from one place.
-   For adverts. This way, you can apply them site-wide or on individual pages.
-   To manage links in a global area of the site. For example, in the footer.
-   For calls to action, such as newsletter sign-up blocks, that may be consistent across many different pages.

## The Snippets menu

You can access the snippets by clicking **Snippets** in the [Sidebar](/en-latest/how-to-guides/find-your-way-around/). Clicking **Snippets** takes you to the [Snippets interface](/en-latest/concepts/wagtail-interfaces/).

## Viewing snippets

Clicking a snippet type will display all of its items.

![Snippets listing for countries](https://guide-media.wagtail.org/images/Snippets_listing_for_countries.width-900.png)

In this listing view, it’s entirely up to site implementers to decide which attributes of the snippets are displayed, used for sorting, available for searching and filtering.

When configured this listing view can also be used to reorder the items of a snippet:

![Snippets listing for countries with manual reordering support](https://guide-media.wagtail.org/images/Snippets_listing_for_countries_with_manual_reo.width-900.png)

## Adding and editing

To add, edit, or delete a snippet, click the snippet type that interests you. Clicking the snippet type takes you to the [edit screen](/en-latest/concepts/wagtail-interfaces/), from which you can add, edit, or delete a snippet. Hovering over an individual snippet displays the options to edit or delete that snippet. To add a new snippet to the snippet type, click **Add (snippet type)**.

![Snippets listing, with five rows. For each row, we show the snippets name and number of instances](https://guide-media.wagtail.org/images/Snippets_listing_with_five_rows._For_each_row_.width-900_rsCGlq7.png)

Warning: Editing a snippet changes it on all of the pages on which it appears. In the top-right corner of the Snippet [edit screen](/en-latest/concepts/wagtail-interfaces/), you can see a label saying how many times you have used the snippet. Clicking this label displays a listing of all of these pages.

## Add snippets while editing a page

When editing a page, you may find yourself in need of a new snippet. Don't worry, Wagtail has this covered. You can create a new one without leaving the page you are editing.

Open the [Snippets interface](/en-latest/concepts/wagtail-interfaces/) in a new tab while editing the page by pressing Ctrl+click in Windows or cmd+click in macOS. You can also open a new tab by right-clicking it and then selecting the **Open in new tab** option. Add the new snippet from this new tab as you normally would. Then return to your existing tab and reopen the Snippet chooser window by clicking **Snippets** from the [Sidebar](/en-latest/how-to-guides/find-your-way-around/).

Congratulation, you can now see your new snippet, even though you didn’t leave the edit page.

![Snippet editing form for a People snippet instance. To the right of the form is a "Usage Used n times" label](https://guide-media.wagtail.org/images/Snippet_editing_form_for_a_People_snippet_inst.width-900.png)

Note: Even though this is possible, it is advisable to save your page as a draft as often as possible. This prevents you from accidentally exiting the edit page and losing your changes.
