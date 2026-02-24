const Button = ({ children, onClick, type = "primary", disabled = false }) => {

  const styles = {
    primary: "bg-blue-600 text-white",
    danger: "bg-red-600 text-white",
    success: "bg-green-600 text-white",
    secondary: "bg-gray-500 text-white"
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded cursor-pointer ${styles[type]} ${disabled ? "opacity-50" : ""}`}
    >
      {children}
    </button>
  );
};

export default Button;
