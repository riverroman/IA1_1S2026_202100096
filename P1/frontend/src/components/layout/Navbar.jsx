import { useNavigate } from "react-router-dom";
import Button from "../common/Button";

const Navbar = () => {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <nav className="w-full bg-white shadow-md px-6 py-4 flex justify-between items-center">
      <div className="text-xl font-bold text-blue-700">
        Medi<span className="text-teal-600">Logic</span>
      </div>

      <div className="flex items-center gap-4">
        {user && (
          <span className="text-gray-600 font-medium">
            {user.name}
          </span>
        )}

        {user && (
          <Button
            onClick={handleLogout}
            type="danger"
          >
            Logout
          </Button>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
