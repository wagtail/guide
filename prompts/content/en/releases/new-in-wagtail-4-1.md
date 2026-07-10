# New in Wagtail 4.1

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-4-1/

> With Wagtail 4.0 and 4.1, we&#39;ve added many substantial updates to the Wagtail page editor as well as some other tools that support every member of a content team.

Wagtail is a lot like a local library — it's packed with amazing resources and nearly everyone will find something they love inside it. Developers love how extendable the code is, content creators enjoy the writer-focused interface, and administrators appreciate the reports and logging tools that help them keep track of their users and all of the content they create.

With Wagtail 4.0 and 4.1, we've added many substantial updates to the Wagtail page editor as well as some other tools that support every member of a content team — from the system administrator who manages the content up to the business owner who hits the publish button on a new article. Let's explore some of the new features and changes you can find in the newest versions of Wagtail.

## Onboarding documentation when you need it

![Wagtail dashboard with new "Things in Wagtail 4 have changed" banner](https://guide-media.wagtail.org/images/Wagtail_dashboard_with_new_Things_in_Wagtail_4.width-900.png)

Starting in Wagtail 4.1, we introduce a new “Help” menu item, with links to user documentation. Those links can be customised for each project, or point to Wagtail’s official guides.

We’ve also added a prominent banner to the dashboard, so people using a new version of Wagtail for the first time get a clear call to action to check out the documentation.

## A fully redesigned page editor

When you sign in, one of the first things you'll notice in Wagtail 4.0 is that the page editor experience has been completely redesigned and updated. Thanks to [generous support from Google](https://www.prnewswire.com/news-releases/google-sponsors-wagtail-cmss-next-generation-web-content-management-experience-301473717.html), all of the styling, forms and widgets have been updated to provide content creators with a seamless, pleasing editing experience. StreamField has been revamped to provide a smoother process for creating content and to make it easier for blocks to be nested inside each other. You'll also notice that all the sections of the page editor are collapsible by default, which will help reduce the amount of scrolling you have to do for longer pieces of content. Because – let's just be honest – _no one_ actually likes scrolling unless they're scrolling through TikTok videos of baby animals.

![Page editor for "Breads and Circuses" blog page, with the info side panel opened to the right, showing the page’s metadata](https://guide-media.wagtail.org/images/Page_editor_for_22Breads_and_Circuses22_blog_p.width-900_aWwHuBl.png)

In Wagtail 4.1, we went one step further and introduced a new toggle to collapse all sections of the page at once, as well as a _minimap_ component. This summarises all of the sections of the page to make it easier to navigate long pages, and validation errors straightforward to locate.

![Page editor for "Breads and Circuses" blog page, with the minimap opened to the right, showing the form sections](https://guide-media.wagtail.org/images/Page_editor_for_22Breads_and_Circuses22_blog_p.width-900_rxHi1iC.png)

## Richer rich text

While updating the page editor, many new features and updates were made to the rich text editor as well. Content creators can now access formatting options and blocks with a “/” slash command. Writers who are tired of highlighting and clicking formatting buttons will love this feature because now you can switch from paragraph text to a numbered list to a heading to a paragraph again without your fingers leaving the keyboard. You can also use the slash command, or the little green plus button that it activates, to split blocks in two and add new blocks in the middle of existing blocks.

![This is a screenshot demonstrating the new slash command you can use in the Rich Text editor of Wagtail](https://guide-media.wagtail.org/images/This_is_a_screenshot_demonstrating_the_new_sla.width-900_uJFDAUA.png)

Link creation is now automatic too. When you paste a URL into a rich text editor, a link will automatically be created rather than having to manually add the link to the URL each time. We also made it easier to undo automatic formatting changes, like the addition of a numbered list when you type “1.” The Wagtail 4 rich text editor also has stronger support for right-to-left languages.

One other useful update to the rich text editor that will make fans of brevity happy is the optional character count feature that can be displayed underneath the rich text editor. So if you have writers who consistently go over character limits, now they can easily track how many characters are contained in each rich text block they're working on. You can even give your writers a gentle nudge if you want by changing the help text to “Brevity is the soul of wit”.

## Enhanced accessibility and support for Windows High Contrast mode

Some of the biggest improvements to this release are ones that many users might not notice right away. But we're hoping users who navigate with keyboards or screen readers will have an improved experience from the efforts we made to provide consistent locations for the help text and error messages throughout the user interface. We also made the tooltips more accessible and improved the accessibility of the sign-in page for Wagtail by improving its structure as well as adding a skip link and messages for screen readers.

The biggest accessibility win for Wagtail 4.0 is the improved support we added for Windows High Contrast mode. Windows High Contrast mode is a feature that users with low vision or photosensitivity find very useful. With the new improvements, Wagtail has more styles designed to comply with the colours required by Windows High Contrast mode users and will provide them with a more pleasant experience.

## A new way to preview

Rather than opening a whole new tab or page to preview your content, Wagtail 4.0 comes with a live preview panel that can be opened within the page editor. With this panel, content creators can also get a quick view of what their page will look like on multiple displays without having to fuss with browser tools. With just a couple of clicks, you can quickly see how your page will look on mobile, tablet and desktop displays. You can still open a full page preview if that is your preference, but we think you'll enjoy the new preview panel so much that you might never want to click out of the editor.

![Page editor for "Bread and Circuses" page. The form to the left, and to the right the Preview side panel is expanded, showing the page as it would appear to users on Mobile devices](https://guide-media.wagtail.org/images/Page_editor_for_Bread_and_Circuses_page_The_fo.width-900.png)

## Simplified scheduled publishing

In Wagtail 4.1, scheduled publishing is much simpler. Available from the Info side panel, setting a schedule now directly saves the page, and the Info side panel is updated with the expected publication (and expiry) times.

## Colour the admin your way

Don't like the colours we chose for the new default theme? Want to provide some custom branding for your organisation's version of Wagtail? Need to provide extra contrast for your users? Wagtail 4.0 now comes with built-in variables for custom theming. Also, if you _really_ miss the teal and don't share our newfound love for indigo, you can switch it back. We might be just a little bit sad if you do that, but you do you and have fun creating your own colour combos.

## Usage reports

In past versions, getting usage information for different types of content required configuration by developers, and had a clear performance cost. As of Wagtail 4.1 this is now always-on, and snappy, regardless of the size of the site.

Here is what usage counts looks like for a snippet:

![Snippet editing form for a People snippet instance. To the right of the form is a "Usage Used 2 times" label](https://guide-media.wagtail.org/images/Snippet_editing_form_for_a_People_snippet_inst.width-900.png)

## Supercharged snippets

Paying closer attention to the above screenshot, there’s a lot more now happening with snippets! If configured, they can keep track of their history of changes and have drafts, as well as scheduled publishing.

## Global settings for multi-site installations

Multi-site enthusiasts rejoice! With the introduction of global settings models, you will no longer have to enter settings over and over again for each site in your installation. With a new model called _BaseGenericSetting,_ you can define shared settings for multiple sites rather than repetitively adding settings for each individual site. This new feature is as DRY as they come — so dry, it makes the Sahara Desert jealous.
