import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedPage from './components/Protected';
import MeetingDashboard from './components/MeetingDashboard';
import LogoutButton from './components/LogoutButton';



const App = () => {
  return (
    <Router>
      <LogoutButton />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            localStorage.getItem('token') ? (
              <MeetingDashboard />
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
};

export default App;
