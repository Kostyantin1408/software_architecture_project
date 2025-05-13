import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL_SLOTS;

const JoinMeetings = () => {
  const [freeSlots, setFreeSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [email, setEmail] = useState(''); // Store email input
  const [startTime, setStartTime] = useState(''); // Store start time input
  const [endTime, setEndTime] = useState(''); // Store end time input
  const [shouldSearch, setShouldSearch] = useState(false); // State to track search trigger

  useEffect(() => {
    const fetchFreeSlots = async () => {
      if (!shouldSearch) return; // Don't fetch if the search button wasn't clicked

      try {
        setLoading(true);
        const params = {};
        if (email) params.email = email; // Only add email filter if provided
        if (startTime) params.start_time = startTime; // Only add start_time filter if provided
        if (endTime) params.end_time = endTime; // Only add end_time filter if provided

        const res = await axios.get(`${API_URL}/slots/free`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          params: params, // Pass only provided filters as query params
        });
        setFreeSlots(res.data);
      } catch (err) {
        setError('Failed to load available slots. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchFreeSlots();
  }, [shouldSearch]); // Only trigger effect when shouldSearch changes

  const handleSelectSlot = (slot) => {
    setSelectedSlot(slot);
  };

  const handleBookSlot = async () => {
    if (!selectedSlot) {
      setError('Please select a slot to book.');
      return;
    }

    try {
      await axios.post(
        `${API_URL}/slots`,
        {
          start_time: selectedSlot.start_time,
          end_time: selectedSlot.end_time,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
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
    setShouldSearch(true); // Trigger the search when the button is clicked
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
      <input
        type="datetime-local"
        value={startTime}
        onChange={(e) => setStartTime(e.target.value)}
        style={styles.timeInput}
      />
      <input
        type="datetime-local"
        value={endTime}
        onChange={(e) => setEndTime(e.target.value)}
        style={styles.timeInput}
      />

      {/* Search Button */}
      <button onClick={handleSearch} style={styles.searchButton}>
        Search
      </button>

      {/* Show loading or error messages */}
      {loading ? (
        <p style={styles.loading}>Loading available slots...</p>
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
