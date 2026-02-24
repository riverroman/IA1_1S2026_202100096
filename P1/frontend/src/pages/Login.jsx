import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion"
import Button from "../components/common/Button";

function Login() {

  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();

    if (username === "admin" && password === "admin123") {

      const user = {
        name: "Administrador",
        role: "ADMIN"
      };

      localStorage.setItem("user", JSON.stringify(user));

      navigate("/admin");
    } else {
      setError("Credenciales incorrectas");
    }
  };

  return (
    <motion.div
      initial={{ backgroundColor: "#f3f4f6" }}
      animate={{ backgroundColor: "#dbeafe" }}
      transition={{ duration: 1 }}
      className="min-h-screen flex items-center justify-center"
    >
      <motion.form
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="bg-white p-8 rounded-xl shadow-xl w-1/4"
      >

        <h2 className="text-2xl font-bold text-center mb-6">
          Acceso Administrador
        </h2>

        {error && (
          <motion.p
            initial={{ x: -10, opacity: 0 }}
            animate={{ x: [-10, 10, -8, 8, 0], opacity: 1 }}
            transition={{ duration: 0.4 }}
            className="text-red-500 mb-4 text-sm text-center font-bold"
          >
            {error}
          </motion.p>
        )}

        <div className="mb-4">
          <label className="block text-gray-600 mb-1">
            Usuario
          </label>
          <input
            type="text"
            className="w-full border px-3 py-2 rounded"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

        <div className="mb-6">
          <label className="block text-gray-600 mb-1">
            Contraseña
          </label>
          <input
            type="password"
            className="w-full border px-3 py-2 rounded"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <div className="flex justify-between">
          <motion.div whileTap={{ scale: 0.95 }}>
            <Button type="primary" htmlType="submit">
              Iniciar Sesión
            </Button>
          </motion.div>
          <motion.div whileTap={{ scale: 0.95 }}>
            <Button onClick={() => navigate("/")} type="secondary">
              Regresar
            </Button>
          </motion.div>
        </div>
      </motion.form >
    </motion.div >
  );
}

export default Login;
