import { NavLink } from "react-router-dom";

const Sidebar = () => {
  return (
    <aside className="w-64 h-screen bg-slate-900 text-white flex flex-col p-6">
      <h2 className="text-2xl font-bold mb-8 text-blue-400">
        Admin Panel
      </h2>

      <nav className="flex flex-col gap-4">

        <NavLink
          to="/admin"
          className={({ isActive }) =>
            `px-4 py-2 rounded transition ${isActive
              ? "bg-blue-600"
              : "hover:bg-slate-700"
            }`
          }
        >
          Dashboard
        </NavLink>

        <NavLink
          to="/admin/diseases"
          className={({ isActive }) =>
            `px-4 py-2 rounded transition ${isActive
              ? "bg-blue-600"
              : "hover:bg-slate-700"
            }`
          }
        >
          Enfermedades
        </NavLink>

        <NavLink
          to="/admin/symptoms"
          className={({ isActive }) =>
            `px-4 py-2 rounded transition ${isActive
              ? "bg-blue-600"
              : "hover:bg-slate-700"
            }`
          }
        >
          Síntomas
        </NavLink>

        <NavLink
          to="/admin/medications"
          className={({ isActive }) =>
            `px-4 py-2 rounded transition ${isActive
              ? "bg-blue-600"
              : "hover:bg-slate-700"
            }`
          }
        >
          Medicamentos
        </NavLink>

      </nav>
    </aside>
  );
};

export default Sidebar;
