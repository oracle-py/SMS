import React from 'react';

function ErrorMessage({ message, onRetry }) {
  return (
    <div style={{
      backgroundColor: '#fef2f2',
      border: '1px solid #fecaca',
      borderRadius: '8px',
      padding: '20px',
      textAlign: 'center',
    }}>
      <div style={{
        fontSize: '3rem',
        marginBottom: '10px',
      }}>
        ⚠️
      </div>
      <div style={{
        color: '#dc2626',
        fontSize: '1.125rem',
        fontWeight: '600',
        marginBottom: '10px',
      }}>
        Error
      </div>
      <div style={{
        color: '#991b1b',
        fontSize: '0.875rem',
        marginBottom: '20px',
      }}>
        {message}
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            backgroundColor: '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            padding: '10px 20px',
            cursor: 'pointer',
            fontSize: '0.875rem',
            transition: 'background-color 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#b91c1c';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#dc2626';
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
}

export default ErrorMessage;
