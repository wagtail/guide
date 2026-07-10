# Configure workflows for moderation

Page URL: https://guide.wagtail.org/en-latest/how-to-guides/configure-workflows-for-moderation/

> Workflows allow you to configure how moderation works on your site. Workflows are sequences of tasks, all of which must be approved before the workflow completes (by default, this results in the publication of the page, but depends on your site settings).

## About workflows

Workflows allow you to configure how moderation works on your site. Workflows are sequences of tasks that require approval before completion. A completed workflow usually results in the publication of a page, depending on your website's settings.

To access the Workflow interface, go to **Settings > Workflows** from the [Sidebar](/en-latest/how-to-guides/find-your-way-around/).

![Listing of workflows with a single Moderators approval workflow shown that has a single step](https://guide-media.wagtail.org/images/Listing_of_workflows_with_a_single_Moderators_.width-900_BfEuku6.png)

From the [Workflow interface](/en-latest/concepts/wagtail-interfaces/), you can see all of the workflows on your site and the order of tasks in each. To create a new workflow, click **Add a workflow** from the [Workflow interface](/en-latest/concepts/wagtail-interfaces/).

Furthermore, the [Workflow interface](/en-latest/concepts/wagtail-interfaces/) shows how many pages each workflow covers. If you click the number of pages, you can see a list of all the pages a workflow applies to.

## **Edit workflows**

In the [Workflow interface](/en-latest/concepts/wagtail-interfaces/), click on the name of a workflow to edit it or to assign it to a part of the page tree.

Click **Add task** under **Add tasks to your workflow** to add a task. When adding a task to a workflow, you can create a new task or reuse an existing one.

To change a task in the workflow, hover over the task under **Add tasks to your workflow** and select **Choose another task** from the pop-up options.

You can also reorder tasks in a workflow by hovering over a task under the **Add tasks to your workflow** and then clicking the up and down arrow.

Under **Assign your workflow to pages**, you can see a list of the pages assigned to a workflow. All child pages take the same workflow as their parents. So if the root page of your site gets assigned to a workflow, it becomes the default workflow. You may remove a page from the workflow by clicking **Delete** at the right of each entry. Also, you can change the page in an entry to another by clicking **Choose another page**.

The action menu at the bottom allows you to save your changes, or disable the workflow. Disabling a workflow cancels all pages currently in moderation in that workflow, and prevents others from starting it. If the workflow was previously disabled, then you get the option to enable it in the action menu.

![Screenshot of the workflow editing interface with fields to change the workflow name tasks and assigned pages](https://guide-media.wagtail.org/images/Screenshot_of_the_workflow_editing_interface_w.width-900_MbZ7ac3.png)

## Create and edit tasks

To create a task, go to **Settings > Workflows tasks** from the Sidebar. This takes you to the [Tasks interface](/en-latest/concepts/wagtail-interfaces/), where you can see a list of the currently available tasks and which workflows use each task. Similar to workflows, you can click the name of an existing task to edit it. To add a new task, click **Add a task**.

![Tasks listing with a single item](https://guide-media.wagtail.org/images/Tasks_listing_with_a_single_item_MvFdm6B.width-900.png)

When creating a task, if you have multiple task types available, then they are offered to you as options. By default, only _group approval tasks_ are available. By creating a _group approval task_, you are able to select one or multiple groups. Members of any of these, as well as administrators, will be able to approve or reject moderation for this task.

![Tasks creation form with Name field and Groups checkboxes with two Moderators and Editors options](https://guide-media.wagtail.org/images/Tasks_creation_form_with_Name_field_and_Groups.width-900_Sf0WPeH.png)

When editing a task, you may find that some fields, such as the name field, are uneditable. This is to ensure workflow history remains consistent. If you need to change the name of a task, then disable the old task, and create a new one with the name you need. Disabling a task causes any pages currently in moderation on that task to skip to the next task.
