# Manage pages

Page URL: https://guide.wagtail.org/en-latest/how-to-guides/manage-pages/

> Create new pages by clicking the Add child page button. This creates a child page of the section you are currently in. In this case a child page of the &#39;Breads&#39; page.

## Create new pages

To create a new page, click the **Add** button at the top of page. This creates a child page of the section you are currently in. In this case, a child page of the **Breads** page. There are other actions relating to pages available in the **Actions** menu next to the Add button:

![Breads page listing with expanded three dots Actions menu in the header showing 7 different page actions One Add child page is highlighted in red](https://guide-media.wagtail.org/images/Breads_page_listing_with_expanded_three_dots_A.width-900_9Cddamn.png)

## Edit existing pages

You can access an existing page's [edit screen](/en-latest/concepts/wagtail-interfaces/) in three ways.

First, by clicking **… Actions** and then select the Edit option from the dropdown. Second, by clicking the page's title if you are accessing the page from its parent's Explorer page or in search results. Last, if you are accessing the page from the [Explorer page](/en-latest/how-to-guides/find-your-way-around/) of its parent, you can hover over the page and then click Edit.

On the [edit screen](/en-latest/concepts/wagtail-interfaces/), you can find the title of the page you are editing at the top of the page. If the page is already published, then you can find a link to the live version of the page at the top right of the page. To change the title of the page, click the title field and enter a new title.

![Page editor for Bread and Circuses page The form to the left and to the right the Preview side panel is expanded showing the page as it would appear to users on Mobile devices](https://guide-media.wagtail.org/images/Page_editor_for_Bread_and_Circuses_page_The_fo.width-900_cb8HY0Q.png)

## Validation errors

Clicking "Save draft" will save the latest changes as a draft, skipping form fields validation where possible. Clicking "Publish" always runs all available form field validation. When errors are present, they are all displayed directly within the form, with an overview message at the top of the page, including a shortcut to go to the first error:

![Validation error message on page publish with go to first error shortcut button](https://guide-media.wagtail.org/images/Validation_error_message_on_page_publish_with_.width-900.png)

---

## Available actions

While on the [edit screen](/en-latest/concepts/wagtail-interfaces/), you can perform several actions, such as copying, moving, or deleting a page. To perform any of these actions, click **… Actions** at the top of the [edit screen](/en-latest/concepts/wagtail-interfaces/) and select the applicable option from the dropdown.

## Edit block content

Wagtail’s block-based editing is called StreamField. It’s a key feature of the CMS, that gives editors creative control over content.

![Close-up of a rich text block with a text paragraph and then a thumbnail with a video Play symbol in the top right](https://guide-media.wagtail.org/images/Close-up_of_a_rich_text_block_with_a_text_para.width-900.png)

Within block-based StreamField, editors can:

-   Insert blocks – as a list where all blocks are of the same type, or as a stream with multiple supported block types.
-   Reorder blocks – with up and down controls, or drag and drop.
-   Duplicate blocks - to speed up content entry.
-   Remove blocks.

Within blocks, the same fields are used as other aspects of the page. Or often, blocks can be nested within other blocks.

The same block-based interface is also available for more structured data, often combined with [snippets](/en-latest/how-to-guides/manage-snippets/), with minor differences in capabilities (for example absence of "duplicate" option:

![Authors block with two Authors child items each containing a People field The first blocks controls to the right are highlighted in red](https://guide-media.wagtail.org/images/Authors_block_with_two_Authors_child_items_eac.width-900.png)

### Block chooser

Clicking the "+" Add button, the block chooser appears. It allows the user to choose between available block types, which vary depending on configuration of the page and field.

![Block chooser in StreamField, with a block being previewed](https://guide-media.wagtail.org/images/block_chooser_and_preview_focus.width-900.png)

If configured, blocks can display a preview of how they would display on the site and description of their intended use.

## Create and edit comments

To toggle on commenting mode, click **Comments** at the top of the [edit screen](/en-latest/concepts/wagtail-interfaces/) page. Once commenting mode is on, you can create a new comment or reply to a comment by hovering over any commentable field to reveal the add comment icon.

![Screenshot of a Subtitle form field with a comment button next to it highlighted in red](https://guide-media.wagtail.org/images/Screenshot_of_a_Subtitle_form_field_with_a_com.width-900_debqfyS.png)

If there is no pre-existing comment in the field, click the add comment icon to create a new comment. However, if there is an existing comment, clicking either the field button or the comment brings the comment thread into focus. This allows you to add new replies.

![Two form fields with a comment pop-up off to the right side](https://guide-media.wagtail.org/images/Two_form_fields_with_a_comment_pop-up_off_to_t.width-900_wlOeHj8.png)

To comment on the text within the rich text field, highlight the text and then click the add comment icon to add an inline comment.

!["Heat is gradually" text selection within a rich text editor. Above the selection, the inline toolbar shows, with a "bubble" icon comment button to the right in teal](https://guide-media.wagtail.org/images/22Heat_is_gradually22_text_selection_within_a_.width-900_cemT3h0.png)

Alternatively, you can perform all of these actions using the comment shortcut, Ctrl + Alt + M on Windows and ⌘ + Alt + M on macOS.

To edit, delete, or resolve a comment, click the three vertical dots in the top right of an existing comment and select the applicable option. Saving the page after leaving a comment or replying to a comment saves the comment or reply.

![A comment pop-up, with its three dots "actions" menu expanded, with Edit, Delete, Resolve options](https://guide-media.wagtail.org/images/A_comment_pop-up_with_its_three_dots_22actions.width-900_SlOlf6V.png)

Note: Currently, fields inside **InlinePanels** and **ListBlocks** are uncommentable.

The arrow to the right of the comments icon shows the comment notifications
panel, where you can enable or disable email notifications for other users' comments on the page.

![Wide screenshot of the page editors tabs and the comment notifications switch off to the right](https://guide-media.wagtail.org/images/Wide_screenshot_of_the_page_editors_tabs_and_t.width-900_yxd4W35.png)

Note: You will always receive email notifications for threads you are part of, unless you opt out of all comment notifications in your account settings.

All participants in a thread will receive email notifications for new replies, even if they no longer have permission to edit the page.

## Concurrent editing notifications

![Concurrent editing warning dialog to prevent unintentional overrides](https://guide-media.wagtail.org/images/Concurrent_editing_warning_dialog_to_prevent_u.width-900.png)

When multiple users concurrently work on the same content, Wagtail displays notifications to inform them of potential editing conflicts. Those notifications initially appear as user avatars in the page header, each with a status tooltip.

When a user saves their work, other users are informed and presented with options: they can refresh the page to view the latest changes, or proceed with their own changes, overwriting the other user's work.

![Concurrent editing overwrite confirmation dialog](https://guide-media.wagtail.org/images/overwrite_confirmation_dialog.width-900.png)

Users are displayed as "active" in concurrent editing notifications until they switch to another application or close the browser tab, or after a set timeout.

## Manage page privacy

Users with publish permission on a page can set it to be private by clicking the ‘Change privacy’ control in the status panel. This sets a restriction on who is allowed to view the page, and its [child pages](/en-latest/concepts/pages/). Several options are available:

-   **Public**: the page is accessible to anyone who can access the website.
-   **Accessible to any logged-in users:** The user must log in to view the page. All user accounts are granted access, regardless of permission level.
-   **Accessible with a shared password:** The user must enter the given shared password to view the page. This is appropriate for situations where you want to share a page with a trusted group of people, but giving them individual user accounts would be overkill. The same password is shared between all users, and this works independently of any user accounts that exist on the site.
-   **Accessible to users in specific groups:** The user must be logged in, and a member of one or more of the [specified groups](/en-latest/how-to-guides/manage-users-and-roles/), in order to view the page.

Warning: Shared passwords should not be used to protect sensitive content, as the password is shared between all users, and stored in plain text in the database. Where possible, it’s recommended to require users log in to access private page content.

## **Manage page history**

Wagtail allows you to retrieve the version of the content you previously saved as a draft or published. You can do this by hovering over a page on the [Explorer page](/en-latest/how-to-guides/find-your-way-around/) and clicking **More** from the resulting dropdown options. Alternatively, you can access the page history screen by clicking the **History** icon in the top-right corner when editing a page.

On the page's history screen, you can see all the actions previously done on that particular page and the users that carried out the actions. Also, you can see the date or time that the action occurred.

You can also search for specific versions of your content on the page history screen by applying a filter.

![Page history for Breads and circuses with a listing of actions and a filtering form to the right](https://guide-media.wagtail.org/images/Page_history_for_Breads_and_circuses_with_a_li.width-900_h1DdDZJ.png)

If you want to compare different draft versions, hover over the draft and click **Compare with previous version** or **Compare with current version**.

To replace the current version of the draft with a previous version, hover over the preferred version of your draft on the page history screen and click **Review this version**. Then click **Replace current version** located at the bottom of the screen. This action appears as a _Revert_ action on the page history screen and you can always go back to review it.

![page history replace current draft](https://guide-media.wagtail.org/images/page_history_replace_current_draft_neqsiyo.width-900.png)

## Workflow

If the page is currently in a workflow, then you can see an additional indicator underneath the title showing the current workflow task. Clicking this shows more information about the page's progress through the workflow and any comments left by reviewers.

![The page editing form with its Info side panel opened to the right with a highlight on page workflow metadata](https://guide-media.wagtail.org/images/The_page_editing_form_with_its_Info_side_panel.width-900_IDKppPB.png)

If you have permission to perform moderation actions, for example, approval or requesting changes on the current task. In that case, you can see additional options in the action bar at the bottom of the page.

## Copy pages

Sometimes, you don't need to create a new page from scratch. For example, you may have several pages that are similar in terms of structure but differ in content. In that case, you can copy an existing page and only change the required parts.

![Copy action available when hovering over a page in an explorer page](https://guide-media.wagtail.org/images/Copy_action_available_when_hovering_over_a_pag.width-900_UEKIsmm.png)

To copy an existing page, hover over a page in an [Explorer page](/en-latest/how-to-guides/find-your-way-around/), then click **More** and select **Copy**. Selecting **Copy** from the dropdown takes you to a form where you can enter the title and slug of the copy and also choose its parent page. You then get the option to publish the copy right away and an option to mark the copy as an alias of the original page. Once you have completed the form, click **Copy this page**.

![Copy page form with the options to change the title slug parent page published status and option to create an alias](https://guide-media.wagtail.org/images/Copy_page_form_with_the_options_to_change_the_.width-900_nri0WYZ.png)

Congratulations, you just copied a page. You can now find your copied page on the Explorer page.

## Alias pages

When copying a page, you have the option to mark it as an alias. The content of an aliased page always stays in sync with the original.

This is useful when you want a page to be available in multiple places. For example, if you have a page about Brioche as a child page of Breads, and you want to make the Brioche page available in the Pastries section. One way to do this is to create a copy of the Brioche page and change the parent page to the Pastries page. However, you now need to remember to update this copy each time you modify the original page. If you mark a copy as an alias, Wagtail automatically makes changes to the copy each time you modify and publish the original page.

Creating an alias for an existing page is similar to creating a copy. Hover over a page in the [Explorer page](/en-latest/how-to-guides/find-your-way-around/), click **More**, and then select **Copy**. Selecting **Copy** takes you to the copy page form. On the copy page form, choose another page as the parent page by clicking Choose another page.

![Clicking the change button during the copy page form in order to change the parent of the copied page](https://guide-media.wagtail.org/images/Clicking_the_change_button_during_the_copy_pag.width-900_0wwrJ40.png)

Then, click the **Alias** checkbox and click **Copy this page** to complete the aliasing.

![Clicking on the Copy this page button to confirm aliasing](https://guide-media.wagtail.org/images/Clicking_on_the_Copy_this_page_button_to_confi.width-900_sIikjIn.png)

Congratulations, you just aliased a page. You can now find your aliased page on the [Explorer page](/en-latest/how-to-guides/find-your-way-around/) of the parent page.

If you try to edit the aliased page, you get a notification that it's an alias of another page. To edit an aliased page, you have two options:

-   Edit the original page. This option changes both the original page and the aliased page.
-   Convert the alias page to an ordinary page, which is a copy of the original. If you choose this option, you must make manual changes to the alias page in order for it to be in sync with the original page.
