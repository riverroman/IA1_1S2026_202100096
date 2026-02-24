import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import Button from "../common/Button";

const Navbar = () => {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <motion.nav
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="w-full bg-white shadow-md px-6 py-4 flex justify-between items-center"
    >
      <motion.div
        whileHover={{ scale: 1.05 }}
        className="text-xl font-bold text-blue-700 cursor-pointer"
      >
        Medi<span className="text-teal-600">Logic</span>
      </motion.div>

      <div className="flex items-center gap-4">
        {user && (
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-gray-600 font-medium"
          >
            {user.name}
          </motion.span>
        )}

        {user && (
          <motion.div whileTap={{ scale: 0.95 }}>
            <Button onClick={handleLogout} type="danger">
              Logout
            </Button>
          </motion.div>
        )}
      </div>
    </motion.nav>
  );
};

export default Navbar;
