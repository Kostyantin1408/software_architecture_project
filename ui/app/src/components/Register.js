import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_FACADE_URL;

const Register = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();

    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }
    console.log(`${API_URL}/register`)
    try {
      const res = await axios.post(`${API_URL}/register`, {
        name,
        email,
        password,
      });

      setSuccess('Registration successful! You can now log in.');
      setError('');
      setName('');
      setEmail('');
      setPassword('');
      setConfirm('');
    } catch (err) {
      setError('Registration failed');
      setSuccess('');
    }
  };

  return (
    <div style={styles.container}>
      <h2>Register</h2>
      <form onSubmit={handleRegister} style={styles.form}>
        <input
          type="text"
          placeholder="Full Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          style={styles.input}
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={styles.input}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={styles.input}
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          required
          style={styles.input}
        />
        <button type="submit" style={styles.button}>Register</button>
        {error && <p style={styles.error}>{error}</p>}
        {success && <p style={styles.success}>{success}</p>}
        <p>
          Already have an account?{' '}
          <span style={styles.link} onClick={() => navigate("/login")}>Login</span>
        </p>
      </form>
    </div>
  );
};

const styles = {
  container: { maxWidth: '300px', margin: '100px auto', textAlign: 'center' },
  form: { display: 'flex', flexDirection: 'column', gap: '10px' },
  input: { padding: '10px', fontSize: '16px' },
  button: { padding: '10px', fontSize: '16px' },
  error: { color: 'red' },
  success: { color: 'green' },
  link: { color: 'blue', cursor: 'pointer', textDecoration: 'underline' },
};

export default Register;
