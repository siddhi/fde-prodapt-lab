import type { Route } from "../app/+types/root";

export async function clientLoader() {
  const res = await fetch(`/api/job-boards`);
  const jobBoards = await res.json();
  return {jobBoards}
}

export default function JobBoards({loaderData} : Route.ComponentProps) {
  return (
    <div>
      {loaderData.jobBoards.map((jobBoard) => <p>{jobBoard.slug}</p>)}
    </div>
  )
}