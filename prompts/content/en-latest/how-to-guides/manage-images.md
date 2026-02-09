# Manage images

Page URL: https://guide.wagtail.org/en-latest/how-to-guides/manage-images/

> If you want to edit, add or remove images from the CMS outside of the individual pages you can do so from the Images interface.

## Add, edit, and remove images

If you want to edit, add, or remove images from the [Admin interface](/en-latest/concepts/wagtail-interfaces/) outside of the individual pages, you can do so from the [Images interface](/en-latest/concepts/wagtail-interfaces/). To access the Images interface, click **Images** in the [Sidebar](/en-latest/how-to-guides/find-your-way-around/).

![Images listing with header and images grid](https://guide-media.wagtail.org/images/Images_listing_with_header_and_images_grid_OFs.width-900.png)

Wagtail allows you to select multiple images from the Images interface at once. To do this, select the checkbox on the top left of each image block, then use the bulk actions bar at the bottom to perform an action on all selected images.

![Images listing with checkboxes shown next to images Five images are selected and a bottom menu shows different actions as well as a 5 images selected label](https://guide-media.wagtail.org/images/Images_listing_with_checkboxes_shown_next_to_i.width-900_uduIqfm.png)

Also, Wagtail allows you to edit the data associated with an image by clicking on the image to access its edit screen. Image data includes the title, the file, the collection associated with it, the associated tags, and the focal area.

## List layout

In addition to the default “grid” layout, this interface also supports viewing images in a list, like other listings. This can be useful when working with larger numbers of images.

![Images listing with header and images list](https://guide-media.wagtail.org/images/Images_listing_with_header_and_images_list.width-900.png)

## Image alt text

By default, Wagtail uses the image’s description field as alt text. Alt text is important for screen reader users accessing the site but also the CMS, to get a text description of the image contents.

![Image editing form for Olivia Ava image To the right of the form is an image preview focal point controls and metadata about the image](https://guide-media.wagtail.org/images/Image_editing_form_for_Olivia_Ava_image_To_the.width-900_T2JPY0c.png)

It is also common for site implementers to customize this, either by adding a separate alt text field for all images, or where images are used.

So, to help screen reader users better understand your images, ensure you provide image descriptions or explicitly mark images that are purely decorative.

Warning: Changing the file will change it on all pages that use the image.

## Set the focal area of an image

The Images interface allows you to set a focal area, which can affect how your image displays to visitors on the front end. If you crop your images in some way to make them fit into a specific shape, then the focal area defines the centre point from which you crop the images.

You can set the focal area of an image by clicking the image to access its [edit screen](/en-latest/concepts/wagtail-interfaces/). Then drag a marquee around the most significant element of the image, and then click **Save** to save it. Once you set the focal area of an image and save it, you can see the most significant element of the image on the front end.

To remove the focal area, click **Remove focal area** in the [edit screen](/en-latest/concepts/wagtail-interfaces/).

## Image format requirements

By default, Wagtail supports image uploads in the following file formats: AVIF, GIF, JPG, JPEG, PNG, WebP. Site implementers can also allow fewer formats, or add support for HEIC / HEIF. Wagtail will then convert images to the appropriate format for site users based on configuration by developers.

Wagtail also optimizes image quality based on the needs of site users, per the configuration done by developers. By default, images use a "safe for web" quality setting to apply compression suitable for most use cases from thumbnails to photography. Developers can override this default configuration wherever images are in use, or even display images with "lossless" quality.

### File size requirements

By default, Wagtail limits image uploads to a maximum of 10MB. It also restricts uploading of images larger than 128 megapixels (close to 16K resolution).
