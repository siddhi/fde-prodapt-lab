import { Form, Link, redirect } from "react-router";
import type { Route } from "../+types/root";
import { Field, FieldGroup, FieldLabel, FieldLegend } from "~/components/ui/field";
import { Input, TextArea } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import { useState } from "react";

export async function clientLoader({params}) {
  const jobBoardId = params.jobBoardId
  return {jobBoardId}
}

export async function clientAction({ request }: Route.ClientActionArgs) {
  const formData = await request.formData()
  const reviewed = formData.get('reviewed')
  const job_board_id = parseInt(formData.get('job_board_id'))
  if (reviewed === "true") {
    await fetch('/api/job-posts', {
      method: 'POST',
      body: formData
    })
    return redirect(`/job-boards/${job_board_id}/job-posts`);
  } else {
    const response = await fetch('/api/review-job-description', {
      method: 'POST',
      body: formData
    })
    return response.json();
  }
}

export default function NewJobBoardForm({
  loaderData,
  actionData,
  ...props
}) {
  const [reviewed, setReviewed] = useState("false")
  const [summary, setSummary] = useState("")
  if (actionData && reviewed === "false") {
    setSummary(actionData.overall_summary);
    setReviewed("true")
  }
  return (
    <div className="w-full max-w-md">
      <Form method="post" encType="multipart/form-data">
        <input type="hidden" name="reviewed" value={reviewed} />
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
            <TextArea
              id="description"
              name="description"
              required
            />
          </Field>
          <div>
            {summary}
          </div>
          <div className="float-right">
            <Field orientation="horizontal">
              {reviewed === "false" ? <Button type="submit">Review</Button>: <Button type="submit">Submit</Button>}
              <Button variant="outline" type="button">
                    <Link to={`/job-boards/${loaderData.jobBoardId}/job-posts`}>Cancel</Link>
                  </Button>
            </Field>
          </div>
        </FieldGroup>
      </Form>
    </div>
  );
}