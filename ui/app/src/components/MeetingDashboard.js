import React, { useState } from 'react';
import MySlots from './MySlots';
import JoinMeetings from './JoinMeetings';

function MeetingDashboard() {
  const [currentView, setCurrentView] = useState('slots');

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Meeting App</h1>
      <div style={styles.buttonGroup}>
        <button
          onClick={() => setCurrentView('slots')}
          style={currentView === 'slots' ? styles.activeButton : styles.button}
        >
          My Slots
        </button>
        <button
          onClick={() => setCurrentView('join')}
          style={currentView === 'join' ? styles.activeButton : styles.button}
        >
          Join Meetings
        </button>
      </div>

      <div style={styles.content}>
        {currentView === 'slots' && <MySlots />}
        {currentView === 'join' && <JoinMeetings />}
      </div>
    </div>
  );
}

const styles = {
  container: { maxWidth: '600px', margin: '0 auto', padding: '20px' },
  title: { textAlign: 'center', marginBottom: '20px' },
  buttonGroup: { display: 'flex', justifyContent: 'center', gap: '10px', marginBottom: '20px' },
  button: { padding: '10px 20px', border: '1px solid #0077cc', backgroundColor: 'white', color: '#0077cc', cursor: 'pointer', borderRadius: '4px', transition: 'all 0.2s ease-in-out' },
  activeButton: { padding: '10px 20px', border: '1px solid #0077cc', backgroundColor: '#0077cc', color: 'white', cursor: 'pointer', borderRadius: '4px', transition: 'all 0.2s ease-in-out' },
  content: { marginTop: '20px' },
};

export default MeetingDashboard;
