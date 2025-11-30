import { Form, Link, redirect } from "react-router";
import type { Route } from "../+types/root";
import { Field, FieldGroup, FieldLabel, FieldLegend } from "~/components/ui/field";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import { userContext } from "~/context";

export async function clientLoader({params}) {
  const jobBoardId = params.jobBoardId
  return {jobBoardId}
}

export async function clientAction({ request }: Route.ClientActionArgs) {
  const formData = await request.formData()
  const job_board_id = parseInt(formData.get('job_board_id'))
  await fetch('/api/job-posts', {
    method: 'POST',
    body: formData
  })
  return redirect(`/job-boards/${job_board_id}/job-posts`)
} 

export default function NewJobBoardForm({
  loaderData,
  ...props
}) {
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
            <Input
              id="description"
              name="description"
              required
            />
          </Field>
          <div className="float-right">
            <Field orientation="horizontal">
              <Button type="submit">Submit</Button>
              <Button variant="outline" type="button">
                <Link to="/job-boards">Cancel</Link>
              </Button>
            </Field>
          </div>
        </FieldGroup>
      </Form>
    </div>
  );
}