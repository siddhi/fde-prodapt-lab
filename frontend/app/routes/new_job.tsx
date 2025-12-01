import { Form, Link, redirect } from "react-router";
import type { Route } from "../+types/root";
import { Field, FieldGroup, FieldLabel, FieldLegend } from "~/components/ui/field";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import { Textarea } from "~/components/ui/textarea";
import { useState, useRef } from "react";

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
  const textboxRef = useRef(null)
  const [reviewed, setReviewed] = useState("false")
  const [summary, setSummary] = useState("")
  const [revisedDescription, setRevisedDescription] = useState("")

  const fix_job_description = () => {
      textboxRef.current.value = revisedDescription
  }

  if (actionData && reviewed === "false") {
    setSummary(actionData.overall_summary);
    setRevisedDescription(actionData.revised_description)
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
            <Textarea
              id="description"
              name="description"
              ref={textboxRef}
              required
            />
          </Field>
          {reviewed === "true" ? (
            <div>
            <p>{summary}</p>
            <Button type="button" onClick={fix_job_description}>Fix</Button>
            </div>
          ) : <div></div>}
          
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