import { motion } from "framer-motion";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

const AdminLayout = ({ children }) => {
  return (
    <div className="flex overflow-hidden">
      <Sidebar />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="flex-1 flex flex-col min-h-screen bg-gray-100"
      >
        <Navbar />
        <motion.main
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.4 }}
          className="p-6"
        >
          {children}
        </motion.main>

      </motion.div>
    </div>
  );
};

export default AdminLayout;
