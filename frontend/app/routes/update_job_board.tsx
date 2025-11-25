import { Form, Link, redirect } from "react-router";
import type { Route } from "../+types/root";
import { Field, FieldGroup, FieldLabel, FieldLegend } from "~/components/ui/field";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  const response = await fetch(`/api/job-boards/${params.jobBoardId}`)
  const jobBoard = await response.json()
  return {jobBoard} 
} 

export async function clientAction({ request, params }: Route.ClientActionArgs) {
  debugger
  const formData = await request.formData()
  await fetch(`/api/job-boards/${params.jobBoardId}`, {
    method: 'PUT',
    body: formData,
  })
  return redirect('/job-boards')
} 

export default function EditJobBoardForm({loaderData}: Route.ComponentProps) {
  return (
    <div className="w-full max-w-md">
      <div className="flex">
        <Form method="post" encType="multipart/form-data" className="w-3/4">
          <FieldGroup>
            <FieldLegend>Add New Job Board</FieldLegend>
            <Field>
              <FieldLabel htmlFor="slug">
                Slug
              </FieldLabel>
              <Input
                id="slug"
                name="slug"
                defaultValue={loaderData.jobBoard.slug}
                placeholder="acme"
                required
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="logo">
                Logo
              </FieldLabel>
              <Input
                id="logo"
                name="logo"
                type="file"
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
        {loaderData.jobBoard.logo_url ? <img className="ml-6 w-20 h-20" src={loaderData.jobBoard.logo_url}></img> : <></>}
      </div>
    </div>
  );
}