import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_FACADE_URL;

const MySlots = () => {
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newSlot, setNewSlot] = useState({ start_time: '', end_time: '' });

  // Fetch the slots when the component mounts
  useEffect(() => {
    const fetchSlots = async () => {
      try {
        const res = await axios.get(`${API_URL}/slots?email=${localStorage.getItem('email')}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        setSlots(res.data);
      } catch (err) {
        setError('Failed to load slots. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchSlots();
  }, []);

  // Handle changes in the input fields for new slot creation
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewSlot((prevSlot) => ({
      ...prevSlot,
      [name]: value,
    }));
  };

  // Handle form submission to create a new slot
  const handleAddSlot = async (e) => {
    e.preventDefault();
    if (!newSlot.start_time || !newSlot.end_time) {
      setError('Both start time and end time are required.');
      return;
    }

    try {
      const res = await axios.post(
        `${API_URL}/slots`,
        newSlot,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      setSlots((prevSlots) => [...prevSlots, res.data]); // Add the new slot to the list
      setNewSlot({ start_time: '', end_time: '' }); // Reset the form fields
      setError(''); // Clear any previous errors
    } catch (err) {
      setError('Failed to create new slot. Please try again.');
    }
  };

  return (
    <div style={styles.container}>
      <h2>My Available Slots</h2>
      
      {/* Conditional Rendering for loading, error, and no slots */}
      {loading ? (
        <p style={styles.loading}>Loading...</p>
      ) : error ? (
        <p style={styles.error}>{error}</p>
      ) : slots.length === 0 ? (
        <p>No slots found. Please add a new slot.</p>
      ) : (
        <ul style={styles.slotList}>
          {slots.map((slot) => (
            <li key={slot.slot_id} style={styles.slotItem}>
              {slot.start_time} - {slot.end_time}
            </li>
          ))}
        </ul>
      )}

      <h3>Add a New Slot</h3>
      <form onSubmit={handleAddSlot} style={styles.form}>
        <div style={styles.formGroup}>
          <label>Start Time:</label>
          <input
            type="datetime-local"
            name="start_time"
            value={newSlot.start_time}
            onChange={handleInputChange}
            style={styles.input}
            required
          />
        </div>
        <div style={styles.formGroup}>
          <label>End Time:</label>
          <input
            type="datetime-local"
            name="end_time"
            value={newSlot.end_time}
            onChange={handleInputChange}
            style={styles.input}
            required
          />
        </div>
        <button type="submit" style={styles.button}>Add Slot</button>
      </form>
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    backgroundColor: '#f9fafb',
    maxWidth: '600px',
    margin: '20px auto',
  },
  loading: {
    fontSize: '18px',
    color: '#007bff',
  },
  slotList: {
    listStyle: 'none',
    padding: '0',
    margin: '20px 0',
  },
  slotItem: {
    padding: '10px 0',
    fontWeight: '600',
    borderBottom: '1px solid #ddd',
    color: '#333',
  },
  error: {
    color: 'red',
    fontWeight: 'bold',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    marginTop: '20px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
  },
  input: {
    padding: '8px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px',
  },
  button: {
    padding: '10px 20px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
  },
  buttonHover: {
    backgroundColor: '#0056b3',
  },
};

export default MySlots;
