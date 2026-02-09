# Manage forms

Page URL: https://guide.wagtail.org/en-latest/how-to-guides/manage-forms/

Wagtail provides a flexible form builder module, that allows users to create forms directly from the admin interface without requiring technical expertise.

## Set up and access the form builder

Forms management is an opt-in feature. For developer documentation, see [Form builder in the developer docs](https://docs.wagtail.org/en/stable/reference/contrib/forms/). Once configured, in Wagtail, forms can be configured with the interface to [manage pages](/en-latest/how-to-guides/manage-pages/). Submissions appear in a separate Forms interface.

## Build your form fields

On a page type with forms support, add any necessary form fields. Here are supported field types:

-   Single line text
-   Multi-line text
-   Email
-   Number
-   URL
-   Checkbox
-   Checkboxes
-   Drop down
-   Multiple select
-   Radio buttons
-   Date
-   Date/time
-   Hidden field

And here are the available field configuration options:

-   **Label**: The label of the field for users of the form
-   **Help text**: additional information about the field
-   **Required**: (on/off)
-   **Field type**
-   **Choices**: Comma or new line separated list of choices. Only applicable in checkboxes, radio and dropdown.
-   **Default value**: Comma or new line separated values supported for checkboxes.

Here is an example field configured to be required multi-line text:

![wagtail multi-line text field required](https://guide-media.wagtail.org/images/wagtail_multi-line_text_field_required.width-900.png)

## Configure submission and thank-you settings

After defining the form fields, configure how submissions will be handled. By default all submissions are saved in the CMS, but developers often configure an option to specify an email address for receiving submissions. If available, it’s also important to set up a “thank you” page or customize a success message to acknowledge users after they submit the form. This small detail improves the user experience and confirms that the submission was successful.

## Manage and export submissions

Alongside the form fields, developers may configure a "Forms submissions panel" which includes the number of total submissions for the given form and also a link to the listing of submissions. Otherwise, navigate to the Forms interface which lists all pages with configured forms on the site.

For each form page, all submissions appear in a table, with configured fields. From there, you can:

-   Export submissions as XLSX (Microsoft Excel, Google Sheets, Apple Numbers) or CSV
-   Filter submissions by date
-   Order submissions by ascending or descending date

Here is a screenshot of this interface with sample content:

![wagtail forms data - contact us submissions listing](https://guide-media.wagtail.org/images/wagtail_forms_data_-_contact_us_submissions_li.width-900.png)

## Accessibility tips for forms

To build accessible forms, we recommend to:

-   Keep the number of form fields small, avoiding adding fields unless they are necessary.
-   Provide help text, making it clear how specific fields are meant to be used.
