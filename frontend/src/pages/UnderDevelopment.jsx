import React from 'react';

const UnderDevelopment = ({ feature }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '20px',
      textAlign: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <div style={{
        background: 'white',
        padding: '40px',
        borderRadius: '20px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        maxWidth: '500px',
        width: '100%'
      }}>
        <div style={{
          fontSize: '80px',
          marginBottom: '20px'
        }}>
          🚧
        </div>
        <h1 style={{
          fontSize: '28px',
          color: '#333',
          marginBottom: '15px',
          margin: 0
        }}>
          Under Development
        </h1>
        <p style={{
          fontSize: '16px',
          color: '#666',
          marginBottom: '25px',
          lineHeight: '1.6'
        }}>
          The <strong>{feature}</strong> feature is currently being developed and will be available soon.
        </p>
        <div style={{
          padding: '15px',
          background: '#f0f4ff',
          borderRadius: '10px',
          marginBottom: '20px'
        }}>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: '#555'
          }}>
            We're working hard to bring you this feature. Stay tuned!
          </p>
        </div>
        <button
          onClick={() => window.history.back()}
          style={{
            padding: '12px 30px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '25px',
            fontSize: '16px',
            cursor: 'pointer',
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}
          onMouseOver={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 5px 20px rgba(102, 126, 234, 0.4)';
          }}
          onMouseOut={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = 'none';
          }}
        >
          Go Back
        </button>
      </div>
    </div>
  );
};

export default UnderDevelopment;
