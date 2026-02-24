import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import Button from "../components/common/Button";

function Home() {
  const navigate = useNavigate();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: "easeOut" }
    }
  };

  return (
    <motion.div
      initial={{ backgroundColor: "#f3f4f6" }}
      animate={{ backgroundColor: "#e0f2fe" }}
      transition={{ duration: 1 }}
      className="min-h-screen flex items-center justify-center px-6"
    >
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="text-center max-w-2xl"
      >
        <motion.h1
          variants={itemVariants}
          className="text-5xl font-bold text-blue-700 mb-6"
        >
          MediLogic
        </motion.h1>

        <motion.p
          variants={itemVariants}
          className="text-gray-600 text-lg mb-10"
        >
          Sistema experto de apoyo diagnóstico preliminar basado en lógica Prolog.
          Esta herramienta no sustituye la consulta médica profesional.
        </motion.p>

        <motion.div
          variants={itemVariants}
          className="flex justify-center gap-6"
        >
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button type="primary" onClick={() => navigate("/patient")}>
              Iniciar Diagnóstico
            </Button>
          </motion.div>

          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button type="secondary" onClick={() => navigate("/login")}>
              Acceso Administrador
            </Button>
          </motion.div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}

export default Home;
