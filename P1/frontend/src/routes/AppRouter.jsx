import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "../pages/Home";
import Login from "../pages/Login";
import AdminDashboard from "../pages/AdminDashboard";
import ProtectedRouter from "../components/layout/ProtectedRouter";
import AdminLayout from "../components/layout/AdminLayout";

const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Públicas */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        {/* Admin protegidas */}
        <Route
          path="/admin"
          element={
            <ProtectedRouter role="ADMIN">
              <AdminLayout>
                <AdminDashboard />
              </AdminLayout>
            </ProtectedRouter>
          }
        />

      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;
