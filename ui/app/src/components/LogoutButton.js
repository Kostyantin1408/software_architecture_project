import React from "react";
import { useNavigate } from "react-router-dom";

const LogoutButton = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const buttonStyles = {
    padding: "10px 20px",
    backgroundColor: "#f44336",
    color: "white",
    border: "none",
    borderRadius: "5px",
    fontSize: "16px",
    fontWeight: "bold",
    cursor: "pointer",
    transition: "background-color 0.3s ease, transform 0.2s ease",
    marginLeft: "auto",
    display: "block",
    textAlign: "center",
  };

  const hoverStyles = {
    backgroundColor: "#d32f2f",
    transform: "scale(1.05)",
  };

  return (
    <button 
      onClick={handleLogout} 
      style={buttonStyles} 
      onMouseOver={(e) => e.target.style.backgroundColor = hoverStyles.backgroundColor} 
      onMouseOut={(e) => e.target.style.backgroundColor = buttonStyles.backgroundColor}
    >
      Logout
    </button>
  );
};

export default LogoutButton;
