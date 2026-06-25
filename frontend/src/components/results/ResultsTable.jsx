import React from 'react';

function ResultsTable({ results, loading }) {
  if (loading) {
    return null; // LoadingSpinner handled by parent
  }

  if (!results || results.length === 0) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '48px',
        textAlign: 'center',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        border: '1px solid #e5e7eb',
      }}>
        <div style={{ fontSize: '3rem', marginBottom: '16px' }}>
          📝
        </div>
        <div style={{ color: '#6b7280', fontSize: '1rem' }}>
          No results available
        </div>
      </div>
    );
  }

  // Get all possible keys from the first result to determine columns
  const sampleResult = results[0];
  const columns = Object.keys(sampleResult).filter(key => 
    key !== 'id' && key !== 'student' && key !== 'created_at' && key !== 'updated_at'
  );

  // Format column headers
  const formatHeader = (key) => {
    return key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '24px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      border: '1px solid #e5e7eb',
    }}>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '800px' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
              {columns.map((column) => (
                <th 
                  key={column} 
                  style={{ 
                    textAlign: 'left', 
                    padding: '12px', 
                    color: '#6b7280', 
                    fontSize: '0.875rem', 
                    fontWeight: '600',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {formatHeader(column)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((result, index) => (
              <tr 
                key={index} 
                style={{ 
                  borderBottom: '1px solid #e5e7eb',
                  transition: 'background-color 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f9fafb';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                {columns.map((column) => (
                  <td 
                    key={column} 
                    style={{ 
                      padding: '12px', 
                      color: '#1f2937',
                      fontSize: '0.875rem',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {result[column] !== null && result[column] !== undefined 
                      ? String(result[column]) 
                      : 'N/A'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ResultsTable;
