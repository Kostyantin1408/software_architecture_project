import React, { useState, useEffect } from 'react';
import axios from 'axios';
const API_URL = process.env.REACT_APP_FACADE_URL;

const JoinMeetings = () => {
  const [freeSlots, setFreeSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [email, setEmail] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [shouldSearch, setShouldSearch] = useState(false);

  useEffect(() => {
    setShouldSearch(false); 
    const fetchFreeSlots = async () => {
      if (!shouldSearch) return;
  
      try {
        setLoading(true);

        const res = await axios.get(
          `${API_URL}/slots?email=${email}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`,
            },
          }
        );
  
        setFreeSlots(res.data);
      } catch (err) {
        setError('Failed to load available slots. Please try again.');
      } finally {
        setLoading(false);
      }
    };
  
    fetchFreeSlots();
  }, [shouldSearch]);
  
  const handleSelectSlot = (slot) => {
    setSelectedSlot(slot);
  };

  const handleBookSlot = async () => {
    if (!selectedSlot) {
      setError('Please select a slot to book.');
      return;
    }

    try {
      const res = await axios.post(
      `${API_URL}/booking`,
        {
          slot_id: selectedSlot.slot_id,
          host_email: email,
          participants: [localStorage.getItem("email")],
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          },
        }
      );
      alert('Slot booked successfully!');
      setSelectedSlot(null);
    } catch (err) {
      setError('Failed to book slot. Please try again.');
    }
  };

  const handleSearch = () => {
    setShouldSearch(true); 
  };

  return (
    <div style={styles.container}>
      <h2>Available Slots to Book</h2>

      {/* Email Search Input */}
      <input
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={styles.emailInput}
      />

      {/* Time Interval Inputs */}

      {/* Search Button */}
      <button onClick={handleSearch} style={styles.searchButton}>
        Search
      </button>

      {/* Show loading or error messages */}
      {loading ? (
        <p style={styles.loading}>Enter email and start search</p>
      ) : error ? (
        <p style={styles.error}>{error}</p>
      ) : freeSlots.length === 0 ? (
        <p>No available slots at the moment.</p>
      ) : (
        <ul style={styles.slotList}>
          {freeSlots.map((slot) => (
            <li key={slot.slot_id} style={styles.slotItem}>
              <button
                style={styles.slotButton}
                onClick={() => handleSelectSlot(slot)}
              >
                {slot.start_time} - {slot.end_time}
              </button>
            </li>
          ))}
        </ul>
      )}

      {selectedSlot && (
        <div style={styles.selectedSlotContainer}>
          <h3>Selected Slot</h3>
          <p>
            {selectedSlot.start_time} - {selectedSlot.end_time}
          </p>
          <button style={styles.bookButton} onClick={handleBookSlot}>
            Book Slot
          </button>
        </div>
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
  emailInput: {
    padding: '10px',
    marginBottom: '20px',
    width: '100%',
    borderRadius: '4px',
    border: '1px solid #ddd',
  },
  timeInput: {
    padding: '10px',
    marginBottom: '10px',
    width: '100%',
    borderRadius: '4px',
    border: '1px solid #ddd',
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
  },
  slotButton: {
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    padding: '10px',
    cursor: 'pointer',
    width: '100%',
    textAlign: 'left',
    transition: 'background-color 0.3s ease',
  },
  error: {
    color: 'red',
    fontWeight: 'bold',
  },
  selectedSlotContainer: {
    marginTop: '20px',
    padding: '15px',
    backgroundColor: '#f2f2f2',
    borderRadius: '8px',
    border: '1px solid #ddd',
  },
  bookButton: {
    padding: '12px 20px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    width: '100%',
  },
  searchButton: {
    padding: '12px 20px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    width: '100%',
    marginTop: '10px',
    marginBottom: '20px',
  },
};

export default JoinMeetings;
