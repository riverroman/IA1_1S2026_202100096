import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";

const Sidebar = () => {
  return (
    <motion.aside
      initial={{ x: -80, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="w-64 h-screen bg-slate-900 text-white flex flex-col p-6"
    >
      <motion.h2
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="text-2xl font-bold mb-8 text-blue-400"
      >
        Admin Panel
      </motion.h2>

      <nav className="flex flex-col gap-4">

        {[
          { to: "/admin", label: "Dashboard" },
          { to: "/admin/diseases", label: "Enfermedades" },
          { to: "/admin/symptoms", label: "Síntomas" },
          { to: "/admin/medications", label: "Medicamentos" }
        ].map((item, index) => (
          <motion.div
            key={item.to}
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 + index * 0.1 }}
          >
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                `px-4 py-2 rounded transition-all duration-200 ${isActive
                  ? "bg-blue-600 shadow-md"
                  : "hover:bg-slate-700 hover:translate-x-1"
                }`
              }
            >
              {item.label}
            </NavLink>
          </motion.div>
        ))}

      </nav>
    </motion.aside>
  );
};

export default Sidebar;
