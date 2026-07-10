# Promote search results

Page URL: https://guide.wagtail.org/en-latest/how-to-guides/promote-search-results/

> Promoted search results are an optional Wagtail feature. For details of how to enable them on a Wagtail installation, see Promoted search results.

Note: Promoted search results are an optional Wagtail feature. For details of how to enable them on a Wagtail installation, see [Promoted search results](https://docs.wagtail.org/en/stable/reference/contrib/searchpromotions.html#module-wagtail.contrib.search_promotions).

Wagtail allows you to promote certain search results depending on the keyword or phrase entered by the user when searching. This can be particularly useful when users commonly refer to parts of your organization by an acronym that isn’t in official use. It's also useful if you want to direct users to a page when they enter a certain term related to the page but not included in the text of the page itself.

For example, Wagtail developers can use this feature to direct people who searched for "finances" on a particular Website to the website's _Annual budget review_ page. The word "finances" isn't mentioned in either the title or the body of the target page, so they created a promoted search result for the word "finances" that pushed the _Annual budget review_ page to the top of the search results.

Note: The promoted result only works if the user types _exactly_ the phrase that you have set it up for. If you have variations of a phrase that you want to take into account, then you must create additional promoted results.

To set up promoted search results, go to **Settings > Promoted search results** from the [Sidebar](/en-latest/how-to-guides/find-your-way-around/). The resulting screen displays a list of previously added promoted search keywords. You can add a promoted result by clicking **Add new promoted result** in the top right of the resulting screen.

![Promoted results listing with search field Add button and four results listed under as rows](https://guide-media.wagtail.org/images/Promoted_results_listing_with_search_field_Add.width-900_WUMaHh9.png)

When adding a promoted result, Wagtail provides you with a **Choose from popular search terms** option. This shows you the most popular terms entered by users into your internal search. Use this list to match your existing promoted results so that users are able to find what they're looking for.

![Popular search terms modal dialog with close button search fields and a table showing multiple terms with their respective Views](https://guide-media.wagtail.org/images/Popular_search_terms_modal_dialog_with_close_b.width-900_1CVXDKo.png)

Once you have entered the search keyword or selected from the most popular terms entered by users, complete the process by clicking **Add recommended page**.

You can add multiple results, but be careful about adding too many, as you may end up hiding all of your organic results behind promoted results. This may not be helpful for users who aren’t really sure what they're looking for.

To edit an existing promoted result go to **Settings > Promoted search results** from the [Sidebar](/en-latest/how-to-guides/find-your-way-around/) and then click the search term you want to edit.

![Promoted result editing form with search term field and associated pages](https://guide-media.wagtail.org/images/Promoted_result_editing_form_with_search_term_.width-900_SnsILeD.png)
