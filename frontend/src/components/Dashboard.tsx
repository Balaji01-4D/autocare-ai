import React from 'react';

interface DashboardProps {}

const Dashboard: React.FC<DashboardProps> = () => {
  return (
    <div style={{ 
      padding: '40px', 
      textAlign: 'center', 
      background: '#ffffff',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center'
    }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>
        Welcome to AutoCare AI Dashboard!
      </h1>
      <p style={{ color: '#666', fontSize: '18px' }}>
        You have successfully logged in.
      </p>
      <button 
        onClick={() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/';
        }}
        style={{
          marginTop: '30px',
          padding: '12px 24px',
          border: 'none',
          borderRadius: '8px',
          background: '#ffdd57',
          color: '#000',
          fontWeight: 'bold',
          cursor: 'pointer',
          fontSize: '16px'
        }}
      >
        Logout
      </button>
    </div>
  );
};

export default Dashboard;
