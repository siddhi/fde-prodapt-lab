import { Link } from "react-router";
import { Button } from "~/components/ui/button";

export async function clientLoader({params}) {
  const res = await fetch(`/api/job-boards/${params.jobBoardId}/job-posts`);
  const jobPosts = await res.json();
  return {jobBoardId: params.jobBoardId, jobPosts}
}

export default function JobPosts({loaderData}) {
  const {jobBoardId, jobPosts} = loaderData;
  return (
    <div>
      <div className="float-right">
        <Button>
          <Link to={`/job-boards/${jobBoardId}/add-job`}>Add New Job</Link>
        </Button>
      </div>
      <div className="space-y-8">
        {jobPosts.map(
          (jobPost) => 
            <div>
              <div className="flex items-center justify-between">
                <h2 key={jobPost.id} className="text-3xl font-bold">{jobPost.title}</h2>
                <Button variant="outline">
                  <Link to={`/job-posts/${jobPost.id}/application`}>Apply</Link>
                </Button>
              </div>
              <p className="mt-2">{jobPost.description}</p>
            </div>
        )}
      </div>
    </div>
  )
}

