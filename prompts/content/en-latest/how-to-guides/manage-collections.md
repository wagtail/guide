# Manage collections

Page URL: https://guide.wagtail.org/en-latest/how-to-guides/manage-collections/

> Access to specific sets of images and documents can be controlled by setting up ‘collections’.

You can control access to specific sets of images and documents by setting up _collections_. By default, all images and documents belong to the _root collection_, but users with appropriate permissions can create new collections from the Collections interface. Go to **Settings > Collections** from the Wagtail [Sidebar](/en-latest/how-to-guides/find-your-way-around/) to access the Collections interface.

![Collections listing with three rows Bakeries BreadPage Images Other](https://guide-media.wagtail.org/images/Collections_listing_with_three_rows_Bakeries_B.width-900_wfcKD0D.png)

## Add a collection

To create a collection, click **Add a collection** from the [Collections interface](/en-latest/concepts/wagtail-interfaces/). Then enter a name in the **Name** field and select a parent. Click **Create** to complete the creation process.

![Form to create a collection with a Name text field and Parent dropdown field](https://guide-media.wagtail.org/images/Form_to_create_a_collection_with_a_Name_text_f.width-900_AjTrT2Z.png)

## Add images or documents to a collection

To add images to a collection, click **Images** from the Wagtail [sidebar](/en-latest/how-to-guides/find-your-way-around/) and select a collection from the **Collections** dropdown. Then click **Add an image** and follow the instructions on the screen.

![Screenshot of the Add Images page with a drag-and-drop zone with the Collection dropdown field highlighted in red](https://guide-media.wagtail.org/images/Screenshot_of_the_Add_Images_page_with_a_drag-.width-900_7O96bkj.png)

The process of adding documents to a collection is similar to that of images. Click **Documents** from the [Sidebar](/en-latest/how-to-guides/find-your-way-around/) and select a collection from the **Collections** dropdown. Then click **Add a document** and follow the instructions on the screen.

It's possible to add an image or document to a collection while editing them. To do this, click **Images** or **Documents** from the [Sidebar](/en-latest/how-to-guides/find-your-way-around/) and select the image or document you want to add to a collection by clicking it. Then choose a collection from the **Collection** dropdown in the [edit screen](/en-latest/concepts/wagtail-interfaces/).

![Screenshot of the image editing form for an image titled Olivia Ava with the Collection field highlighted in red](https://guide-media.wagtail.org/images/Screenshot_of_the_image_editing_form_for_an_im.width-900_wUGdfde.png)

You can also select a collection as part of uploading multiple images or documents.

## Privacy settings

To set permissions to determine who is able to view documents within a collection, go to **Settings > Collections** and select a collection. Then click **Privacy** preceding the collection name.

![The collection editing form for BreadPage Images with a red highlight around the Privacy public form control](https://guide-media.wagtail.org/images/The_collection_editing_form_for_BreadPage_Imag.width-900_aUsWz8h.png)

Clicking **Privacy** gives you a pop-up modal from which you can select the level of privacy for the collection.

![Change privacy modal dialog, with four options as radio buttons](https://guide-media.wagtail.org/images/Change_privacy_modal_dialog_with_four_options_.width-900_KDRvPGs.png)

The permissions set on a collection apply to that collection and all collections below it in the hierarchy. Therefore, if you make the _root_ collection private, all documents on the site become private. Permissions set in other collections only apply to those collections.

Note: Privacy settings added to a collection are only enforced for documents within the collection. Privacy settings do not apply to images.
