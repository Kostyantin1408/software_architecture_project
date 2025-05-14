import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_FACADE_URL;

const MySlots = () => {
  const [slots, setSlots] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(true);
  const [loadingBookings, setLoadingBookings] = useState(true);
  const [error, setError] = useState('');
  const [newSlot, setNewSlot] = useState({ start_time: '', end_time: '' });

  // Fetch slots
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
        setError('Failed to load slots.');
      } finally {
        setLoadingSlots(false);
      }
    };

    fetchSlots();
  }, []);

  // Fetch bookings
  useEffect(() => {
    const fetchBookings = async () => {
      try {
        const res = await axios.get(`${API_URL}/bookings`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        setBookings(res.data);
      } catch (err) {
        setError('Failed to load bookings.');
      } finally {
        setLoadingBookings(false);
      }
    };
    fetchBookings();
  }, []);


  const handleDelete = async (slotId) => {
    try {
      const response = await axios.delete(`${API_URL}/slots/${slotId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
  
      console.log('Slot deleted:', response.data.deleted);
  
      setSlots((prev) => prev.filter((slot) => slot.slot_id !== slotId));
    } catch (error) {
      console.error('Error deleting slot:', error.response?.data || error.message);
    }
  };
  

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewSlot((prevSlot) => ({ ...prevSlot, [name]: value }));
  };

  const handleAddSlot = async (e) => {
    e.preventDefault();
    if (!newSlot.start_time || !newSlot.end_time) {
      setError('Both start time and end time are required.');
      return;
    }

    try {
      const res = await axios.post(`${API_URL}/slots`, newSlot, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setSlots((prev) => [...prev, res.data]);
    } catch (err) {
      setError('Failed to create new slot.');
    }
  };

  return (
    <div style={styles.container}>
      {error && <p style={styles.error}>{error}</p>}

      <h2>My Available Slots</h2>

      {loadingSlots ? (
        <p style={styles.loading}>Loading slots...</p>
      )  : slots.length === 0 ? (
        <p>No slots found. Please add a new slot.</p>
      ) : (
        <ul style={styles.slotList}>
          {slots.map((slot) => (<>
            <li key={slot.slot_id} style={styles.slotItem}>
              {slot.start_time} - {slot.end_time}
            </li> <button
          style={styles.deleteButton}
          onClick={() => handleDelete(slot.slot_id)}
        >
          🗑️
        </button>
      </>
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

      <h2 style={{ marginTop: '40px' }}>My Bookings</h2>

      {loadingBookings ? (
        <p style={styles.loading}>Loading bookings...</p>
      ) : bookings.length === 0 ? (
        <p>No bookings found.</p>
      ) : (
        <ul style={styles.slotList}>
          {bookings.map((booking) => (
            <li key={booking.slot_id} style={styles.slotItem}>
              <strong>Slot ID:</strong> {booking.slot_id}<br />
              <strong>User:</strong> {booking.user_email}<br />
              <strong>Start:</strong> {booking.start_time}<br />
              <strong>End:</strong> {booking.end_time}<br />
              <strong>Participants:</strong> {booking.participants.join(', ')}
            </li>
          ))}
        </ul>
      )}
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
    padding: '10px',
    fontWeight: '500',
    borderBottom: '1px solid #ddd',
    backgroundColor: '#fff',
    borderRadius: '4px',
    marginBottom: '10px',
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
  },
};

export default MySlots;
