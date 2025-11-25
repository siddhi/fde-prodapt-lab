import { NavLink, Outlet } from "react-router";
import logo from "./jobify.png"

export default function DefaultLayout() { 
  const navLinkStyle=
    ({isActive}) => {
      return isActive ? "bg-indigo-100 text-indigo-700 rounded-md px-3 py-2" : "rounded-md px-3 py-2 hover:bg-gray-100"
    }
  return (<main className="">
    <nav className="border-b border-gray-200 bg-white flex space-x-4 p-2 items-center">
      <img src={logo} className="h-12"/>
      <div className="ml-4 space-x-12">
        <NavLink to="/" className={navLinkStyle}>Home</NavLink>
        <NavLink to="/job-boards" className={navLinkStyle}>JobBoards</NavLink>
      </div>
    </nav>
    <div className="p-2 w-1/2 mx-auto my-4"><Outlet/></div>
  </main>);
}

