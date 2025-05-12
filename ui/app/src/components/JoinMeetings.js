import React from 'react';

// Static CSV Data (converted to a JavaScript array)
const meetings = [
  { id: 1, title: 'Team Sync', time: '10:30 AM' },
  { id: 2, title: 'Project Discussion', time: '2:00 PM' },
  { id: 3, title: 'Client Call', time: '4:00 PM' },
];

const JoinMeetings = () => {
  return (
    <div style={styles.container}>
      <h2>Available Meetings to Join</h2>
      <ul style={styles.meetingList}>
        {meetings.map((meeting) => (
          <li key={meeting.id} style={styles.meetingItem}>
            {meeting.title} - {meeting.time}
          </li>
        ))}
      </ul>
    </div>
  );
};

const styles = {
  container: { padding: '15px', border: '1px solid #ccc', borderRadius: '8px', backgroundColor: '#f9f9f9' },
  meetingList: { listStyle: 'none', padding: '0' },
  meetingItem: { padding: '6px 0', fontWeight: '500', borderBottom: '1px dashed #ccc' },
};

export default JoinMeetings;
