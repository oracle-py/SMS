import React from 'react';

function StatusBadge({ status }) {
  const getStatusStyle = (status) => {
    const normalizedStatus = (status || '').toLowerCase();
    
    switch (normalizedStatus) {
      case 'present':
        return {
          backgroundColor: '#10b981',
          color: 'white',
        };
      case 'absent':
        return {
          backgroundColor: '#ef4444',
          color: 'white',
        };
      case 'late':
        return {
          backgroundColor: '#f59e0b',
          color: 'white',
        };
      case 'excused':
        return {
          backgroundColor: '#6366f1',
          color: 'white',
        };
      default:
        return {
          backgroundColor: '#6b7280',
          color: 'white',
        };
    }
  };

  const style = getStatusStyle(status);

  return (
    <span
      style={{
        display: 'inline-block',
        padding: '4px 12px',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: '600',
        textTransform: 'capitalize',
        ...style,
      }}
    >
      {status || 'Unknown'}
    </span>
  );
}

export default StatusBadge;
