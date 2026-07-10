# Pages

Page URL: https://guide.wagtail.org/en-latest/concepts/pages/

> You can use Wagtail Pages to organize the content of your Wagtail websites. It&#39;s common for a typical website to have multiple web pages, and the web pages themselves can have several sections. The same is true for Wagtail pages.

You can use Wagtail Pages to organize the content of your website. It's common for a typical website to have multiple web pages, organized in several sections. The same is true in the CMS. Wagtail pages can have child pages within them. In turn, these child pages can have child pages of their own. You can use this **page tree structure** to represent the sections of the site.

## Wagtail page tree structure

The structure of a Wagtail website is like a tree. At the top of this tree-like structure is a _Root page_ which branches off to several child pages. This is meant to match the information architecture of the website; with the homepage at the top, then "level 1" pages likely reflected in the site’s main menu, and further pages within.

The CMS doesn’t mandate using this tree structure but we find it helps organize larger websites. For developers, it also helps in automatically generating menus, breadcrumbs, listings, and other site navigation features. Our developer documentation covers more of the [page tree theory](https://docs.wagtail.org/en/stable/reference/pages/theory.html).

In the CMS interface, the **Page explorer** allows navigating the site in this tree structure:

![The page explorer with the home page highlighted](https://guide-media.wagtail.org/images/The_page_explorer_with_the_home_page_highlight.width-900_fOh4v2u.png)

### Nature of the relationship between Wagtail pages

To talk about specific areas within the page tree, we use the metaphor of a parent-child relationship between pages. A Wagtail parent page has within it one or more child pages. For instance, in the Admin interface of the Bakery demo, if you click **Pages** from the [Sidebar](/en-latest/how-to-guides/find-your-way-around/), the [Sidebar](/en-latest/how-to-guides/find-your-way-around/) extends to show you the _Welcome to the Wagtail Bakery_ page. The _Welcome to the Wagtail Bakery_ homepage is a parent page. Clicking it takes you to its [Explorer page](/en-latest/how-to-guides/find-your-way-around/), where you can see all the child pages within it.

## Page types

You can have different page types available for you to use in the Admin interface. Developers configure available page types when building the site.

Having multiple page types in your Admin interface allows you to choose the structure you want your page to adopt. You can choose a page type for your pages when you are creating them.

The page type of a parent page may differ from that of the child pages within it. For instance, in the [Admin interface](/en-latest/concepts/wagtail-interfaces/) of the Bakery demo, the page type of the* Welcome to the Wagtail Bakery* page is _Home Page_. Its child page _Breads_ has the _Breads index_ page type, while _Blog_, another child page has the _Blog index_ page type.
