# Lab 1: UI for Add Job

Our ATS app currently only has an API for adding a job to the job board. We do not have a UI for this feature. In this lab, we are going to create the UI.

Creating the UI requires the following steps:

1. Put a "Add Job" button on the job posts page
1. Create a new route for `job-boards/:jobBoardId/add-job`
    * This page should display a "New Job" form
    * Match the form fields to the fields required by the API
    * It should have a submit button and a cancel button
    * Submit button should POST to the backend API
    * Cancel button should go back to the current job board

**Hint**: Use the `new_job_board.tsx` as a reference for this lab

## High level approach

1. Create a job board if you don't alreay have one
1. After adding `Add Job` button, go to the job board and check the button is visible
1. Create a very basic add job page and implement routing. Then verify that clicking `Add Job` button routes correctly to this page
1. Implement the form UI. Load the page and verify that the form is displayed properly. Use developer mode to verify `job_board_id` is set correctly. Verify that cancel button returns to the right page
1. Implement form submission. Reload page and verify that you are able to submit the job. It should appear on the job board
1. Commit and push to github. It should get auto deployed to render. Verify deployment

## Hints

### How do I add a button to job board page?

<details>
<summary>Answer</summary>

Put this jsx on the `job_posts.tsx` page

```jsx
      <div className="float-right">
        <Button>
          <Link to={`/job-boards/${jobBoardId}/add-job`}>Add New Job</Link>
        </Button>
      </div>
```

Note that a react component can only return a single node, so wrap everything inside `<div></div>`
</details>

### How do I create a new route?

<details>
<summary>Answer</summary>

Put this jsx on the `job_posts.tsx` page

```jsx
import { Form, Link, redirect } from "react-router";
import type { Route } from "../+types/root";
import { Field, FieldGroup, FieldLabel, FieldLegend } from "~/components/ui/field";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import { Textarea } from "~/components/ui/textarea";

export default function NewJobBoardForm({
  loaderData,
  actionData,
  ...props
}) {
    return <div>This is new job page</div>
}
```

Then open `routes.ts` and add the route to this page

```js
route("job-boards/:jobBoardId/add-job", "routes/new_job.tsx")
```

Note: Make sure all the commas for each item in the route is proper
</details>

### How do I access the job board id in the page?

<details>
<summary>Answer</summary>

```jsx
export async function clientLoader({params}) {
  const jobBoardId = params.jobBoardId
  return {jobBoardId}
}
```

Then in the component you can access `loaderData.jobBoardId` to get the value
</details>

### What fields should be in the form?

<details>
<summary>Answer</summary>

See class `JobPostForm` in `main.py`
</details>

### What type of field should each form element be?

<details>
<summary>Answer</summary>

* `title` should be an `Input` field
* `description` should be a `Textarea` field
* `job_board_id` should be a hidden field

`description` can be many lines long, so it is better to create it as `Textarea` field

The `job_board_id` value is required by the python API, so we need to submit this value along with the form. But the user should not be able to edit this value. So it should be hidden

* HTML Form Elements: https://www.w3schools.com/html/html_form_input_types.asp
</details>

### We have imported component for Input and Textarea, but not hidden. How to create it?

<details>
<summary>Answer</summary>

Use normal HTML

```jsx
<input type="hidden" name="job_board_id" value={loaderData.jobBoardId} />
```
</details>

### How do I create the form?

<details>
<summary>Hint</summary>

Refer `new_job_board.tsx`
</details>

<details>
<summary>Answer</summary>

```jsx
  return (
    <div className="w-full max-w-md">
      <Form method="post" encType="multipart/form-data">
        <input type="hidden" name="job_board_id" value={loaderData.jobBoardId} />
        <FieldGroup>
          <FieldLegend>Add New Job</FieldLegend>
          <Field>
            <FieldLabel htmlFor="title">
              Title
            </FieldLabel>
            <Input
              id="title"
              name="title"
              placeholder="AI Engineer"
              required
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="description">
              Description
            </FieldLabel>
            <Textarea
              id="description"
              name="description"
              required
            />
          </Field>
          
          <div className="float-right">
            <Field orientation="horizontal">
              <Button type="submit">Submit</Button>
              <Button variant="outline" type="button">
                <Link to={`/job-boards/${loaderData.jobBoardId}/job-posts`}>Cancel</Link>
              </Button>
            </Field>
          </div>
        </FieldGroup>
      </Form>
    </div>
  );
```
</details>

### How do I make API request when clicking Submit button?

<details>
<summary>Hint</summary>

* Implement `clientAction` function
* See `main.py` to find the right API path
* Get job board id from hidden field like this `const job_board_id = parseInt(formData.get('job_board_id'))`
* Redirect to `/job-boards/${job_board_id}/job-posts` after completion
</details>

<details>
<summary>Answer</summary>

```jsx
export async function clientAction({ request }: Route.ClientActionArgs) {
  const formData = await request.formData()
  const job_board_id = parseInt(formData.get('job_board_id'))

  await fetch('/api/job-posts', {
    method: 'POST',
    body: formData
  })
  return redirect(`/job-boards/${job_board_id}/job-posts`);
}
```
</details>

## Discussion Questions

1. How can we test the UI?
1. How can we test it automatically as part of CI/CD?
1. How can we integrate with pytest?
1. What to do if pytest is now taking long time to run?