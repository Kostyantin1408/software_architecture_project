import React from 'react';

// Static CSV Data (converted to a JavaScript array)
const slots = [
  { id: 1, label: '10:15 AM - 10:17 AM' },
  { id: 2, label: '1:30 PM - 1:32 PM' },
  { id: 3, label: '3:00 PM - 3:02 PM' },
];

const MySlots = () => {
  return (
    <div style={styles.container}>
      <h2>My Available Slots</h2>
      <ul style={styles.slotList}>
        {slots.map((slot) => (
          <li key={slot.id} style={styles.slotItem}>
            {slot.label}
          </li>
        ))}
      </ul>
    </div>
  );
};

const styles = {
  container: { padding: '15px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#eef6ff' },
  slotList: { listStyle: 'none', padding: '0' },
  slotItem: { padding: '6px 0', fontWeight: '500', borderBottom: '1px dashed #ccc' },
};

export default MySlots;
