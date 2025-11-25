import { Link } from "react-router";
import { Avatar, AvatarImage } from "~/components/ui/avatar";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "~/components/ui/table";

export async function clientLoader() {
  const res = await fetch(`/api/job-boards`);
  const jobBoards = await res.json();
  return {jobBoards}
}

export default function JobBoards({loaderData}) {
  return (
    <Table className="w-1/2">
      <TableHeader>
        <TableRow>
          <TableHead>Logo</TableHead>
          <TableHead>Slug</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
          {loaderData.jobBoards.map(
          (jobBoard) => 
            <TableRow key={jobBoard.id}>
              <TableCell>
                {jobBoard.logo_url
                ?  <Avatar><AvatarImage src={jobBoard.logo_url}></AvatarImage></Avatar>
                : <></>}
              </TableCell>
              <TableCell><Link to={`/job-boards/${jobBoard.id}/job-posts`} className="capitalize">{jobBoard.slug}</Link></TableCell>
            </TableRow>
        )}
      </TableBody>
    </Table>
  )
}