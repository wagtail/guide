# Accessibility features

Page URL: https://guide.wagtail.org/en-latest/concepts/accessibility-features/

## Global navigation

Wagtail provides multiple navigation components that appear on most pages in the [Admin interface](/en-latest/concepts/wagtail-interfaces/). These components are as follows:

### Skip link

![Wagtail dashboard with the skip link](https://guide-media.wagtail.org/images/Wagtail_dashboard_with_the_skip_link_VKexAHG.width-900.png)

The skip link appears as a **Skip to main content** button in the [Admin interface](/en-latest/concepts/wagtail-interfaces/). If you press the **tab** key of your keyboard on a newly loaded page, the skip link will appear at the top-left corner of your screen. Once the **Skip link** appears, press the **enter** key to activate it. Activating the **Skip link** moves your keyboard focus to the main content of the current page you’re on. This way, you skip over the [Sidebar](/en-latest/how-to-guides/find-your-way-around/) options to the main content.

### Collapsible sections

![Page editor for Breads and Circuses blog page with sections toggle button and anchor links highlighted](https://guide-media.wagtail.org/images/Page_editor_for_Breads_and_Circuses_blog_page_.width-900_QWaiZGW.png)

Collapsible sections make it easier to navigate forms. You can find Collapsible sections on the [Dashboard](/en-latest/how-to-guides/find-your-way-around/) and forms to [manage pages](/en-latest/how-to-guides/manage-pages/). You can use your mouse or keyboard to collapse or expand collapsible sections. The collapsible section anchor link also gives you the link to the section you are working to share with teammates or keep for later.

On forms, you can also **Collapse all** sections in one go, and then **Expand all** or expand individual sections as needed.

![Page editor for Breads and Circuses blog page with the collapse expand all having been clicked](https://guide-media.wagtail.org/images/Page_editor_for_Breads_and_Circuses_blog_page_.width-900_LfZLMSq.png)

### Session time limit

The **session time limit** in the Wagtail CMS works behind the scenes. A session is created when a user logs in. The default time limit is two weeks but can vary depending on the configuration of the CMS.

### Text search

Like most websites, Wagtail supports text search with the use of the Ctrl + F in Windows and **⌘ + F** on macOS. Using the text search feature in the Admin interface searches texts that match your search input in the current tab.

## Keyboard shortcuts

Find all shortcuts supported on your site with the "Keyboard shortcuts" item within the "Help" menu.

![Keyboard shortcuts dialog](https://guide-media.wagtail.org/images/Keyboard_shortcuts_dialog_tWoC6ww.width-900.png)

### Page-level keyboard shortcuts

On all screens, we support:

-   ? to show keyboard shortcuts
-   / to focus the search
-   [ to expand or collapse the main sidebar.
-   Esc to close modal dialogs

On the Edit screen, Wagtail supports additional page-level keyboard shortcuts. These shortcuts are as follows:

-   **⌘ + P** / **Ctrl + P**: This shortcut opens up the Live preview. With the Live preview, you can view the structure of your content in different screen sizes.
-   **⌘ + S** / **Ctrl + S**: This shortcut saves your work as a draft.
-   ] to expand or collapse the mini-map.

### Rich text keyboard shortcuts

Within rich text fields, a large number of shortcuts are available, depending on what type of formatting is enabled within the field. For a full reference, see the [Draftail keyboard shortcuts documentation](https://www.draftail.org/docs/keyboard-shortcuts).

Here are common formatting shortcuts:

-   Paste a URL over selected text to create a link: Ctrl + V / ⌘ + V
-   Insert or edit link with the chooser dialog: Ctrl + K / ⌘ + K
-   Open link: Alt + ↵ / ⌥ + ↵
-   Insert horizontal rule: insert `---`
-   Text formatting (if enabled)
    -   Bold: Ctrl + B / ⌘ + B, or insert `**`
    -   Italic: Ctrl + I / ⌘ + I, or insert `_`
    -   Underline: Ctrl + U / ⌘ + U
    -   Monospace (code): Ctrl + J / ⌘ + J, or insert ```
    -   Strikethrough: Ctrl + ⇧ + X / ⌘ + ⇧ + X, or insert `~`
    -   Superscript: Ctrl + . / ⌘ + .
    -   Subscript: Ctrl + , / ⌘ + ,
-   Block formatting (if enabled)
    -   Apply heading style [1-6]: Ctrl + Alt + [1-6] / ⌘ + ⌥ + [1-6], or insert `##`
    -   Numbered list: Ctrl + ⇧ + 7 / ⌘ + ⇧ + 7, or insert `1.`
    -   Bulleted list: Ctrl + ⇧ + 8 / ⌘ + ⇧ + 8, or insert `-`
    -   Blockquote: insert `>`
    -   Code block: insert `````
-   Insert a comment (if enabled): Ctrl + Alt + M / ⌘ + ⌥ + M

### Bulk selection shortcut

On large listings with bulk editing checkboxes, Wagtail also supports "Shift+Click" selection to mark a large number of items as selected in one go. To use it, keep the Shift or ⇧ key pressed and click on one item to select preceding items.

## Edit screen features

The Edit screen accessibility features are specific to the [Edit screen](/en-latest/concepts/wagtail-interfaces/). These features are as follows:

### Mini-map

The mini-map or “minimap” helps to easily navigate the sections of your content. Placed on the right-hand side of the [Edit screen](https://guide.wagtail.org/en-latest/concepts/wagtail-interfaces/#edit-screen), it contains a list of the different sections within the form and directly links to each of them. Toggle it with the dedicated button, or the ] keyboard shortcut.

The Mini-map also indicates the type of the different sections: headings, subheadings, and blocks within the content.

![Page editor for Breads and Circuses blog page with the minimap opened to the right focused on the toggle](https://guide-media.wagtail.org/images/Page_editor_for_Breads_and_Circuses_blog_page_.width-900_Ve7MRSW.png)

### Editing of headings and elements nesting in rich text fields

This feature allows screen reader users to detect different types of headings within a text block.

### Live preview

Live preview allows you to view the content structure of your work in different screen sizes. Live preview supports mobile, tablet, and desktop screen sizes.

### Command palette

Typing “/” within the body of your content reveals an interface called the Command palette. The Command palette contains features such as:

-   Headings
-   Numbered list
-   Bulleted list
-   Embed
-   Link
-   Document
-   Image
-   Blocks

## User account preferences

User account preferences are settings that are specific to your account. You can access your user account preferences and notification settings from [account settings](/en-latest/reference/account-settings/).

## Browser-level user interface settings

Browser-level user interface settings are stored within your browser. You can adjust these settings based on your preference. If you reload the admin interface or log out and then log back in within the same browser, these settings will remain.

Browser-level user interface settings include the following accessibility settings:

### Sidebar expanded/collapsed

You can expand or collapse the [Sidebar](https://guide.wagtail.org/en-latest/how-to-guides/find-your-way-around/#the-sidebar). Collapsing the Sidebar allows the [Dashboard](https://guide.wagtail.org/en-latest/how-to-guides/find-your-way-around/#the-dashboard) to take up more screen space of the browser. This can also be done with the [ keyboard shortcut.

![The Wagtail sidebar with its minimize control highlighted](https://guide-media.wagtail.org/images/The_Wagtail_sidebar_with_its_minimize_control_.width-900_EMtj2DT.png)

### Rich text toolbar pinned/unpinned

Highlighting text within a rich text field displays a toolbar above the highlighted content. This toolbar contains features such as text bold, text italic, and headings. You can pin this toolbar to be always visible to the top of all rich text fields if you prefer.

![Pin toolbar](https://guide-media.wagtail.org/images/Pin_toolbar.width-900.png)

### **Mini-map expanded/collapsed**

Like the _sidebar expanded/collapsed_, this feature keeps your mini-map opened or closed on your Edit screen, and will be saved across all of your editing sessions Toggle it with the dedicated button, or the ] keyboard shortcut.

![Page editor for Breads and Circuses blog page with the minimap opened to the right focused on the toggle](https://guide-media.wagtail.org/images/Page_editor_for_Breads_and_Circuses_blog_page_.width-900_Ve7MRSW.png)

### Side panel

The Edit screen has a top header. This toolbar contains the following options:

-   **Status**: This indicates the current status of your page. For more information on the various page statuses available, read [Page status](https://guide.wagtail.org/en-latest/concepts/page-status/).
-   **Live Preview**: Live preview allows you to preview content on different screen sizes.
-   **Checks**: Automated checks flagging possible issues with the page content.
-   **Comment**: This notifies and shows you the comments made on your content by teammates.

When you select an option in the toolbar, the selection opens up as a side panel. You can expand or collapse this Side panel, and which panel is active will be saved across editing sessions.

![The page editing form with its Info side panel opened to the right and the Info side panel toggle highlighted](https://guide-media.wagtail.org/images/The_page_editing_form_with_its_Info_side_panel.width-900_RDgRFkj.png)
