import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingSpinner from '../../components/dashboard/LoadingSpinner';
import ErrorMessage from '../../components/dashboard/ErrorMessage';
import ResultsTable from '../../components/results/ResultsTable';
import studentService from '../../services/studentService';

function StudentResults() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sessionFilter, setSessionFilter] = useState('');
  const [semesterFilter, setSemesterFilter] = useState('');

  const fetchResults = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await studentService.getResults();
      setResults(response.data || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  // Get unique sessions and semesters from results
  const sessions = [...new Set(results.map(r => r.session).filter(Boolean))];
  const semesters = [...new Set(results.map(r => r.semester).filter(Boolean))];

  // Filter results
  const filteredResults = results.filter(result => {
    const matchesSearch = searchTerm === '' || 
      (result.course_code && result.course_code.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (result.course_title && result.course_title.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesSession = sessionFilter === '' || result.session === sessionFilter;
    const matchesSemester = semesterFilter === '' || result.semester === semesterFilter;
    
    return matchesSearch && matchesSession && matchesSemester;
  });

  if (loading) {
    return (
      <DashboardLayout userRole="student">
        <LoadingSpinner />
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout userRole="student">
        <ErrorMessage 
          message={error} 
          onRetry={fetchResults}
        />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout userRole="student">
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '20px' }}>
          Academic Results
        </h1>

        {/* Filters and Search */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '24px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          border: '1px solid #e5e7eb',
        }}>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {/* Search */}
            <div style={{ flex: 1, minWidth: '200px' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', color: '#6b7280', marginBottom: '8px' }}>
                Search
              </label>
              <input
                type="text"
                placeholder="Course code or title..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                }}
              />
            </div>

            {/* Session Filter */}
            {sessions.length > 0 && (
              <div style={{ minWidth: '150px' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', color: '#6b7280', marginBottom: '8px' }}>
                  Session
                </label>
                <select
                  value={sessionFilter}
                  onChange={(e) => setSessionFilter(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                  }}
                >
                  <option value="">All Sessions</option>
                  {sessions.map(session => (
                    <option key={session} value={session}>{session}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Semester Filter */}
            {semesters.length > 0 && (
              <div style={{ minWidth: '150px' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', color: '#6b7280', marginBottom: '8px' }}>
                  Semester
                </label>
                <select
                  value={semesterFilter}
                  onChange={(e) => setSemesterFilter(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                  }}
                >
                  <option value="">All Semesters</option>
                  {semesters.map(semester => (
                    <option key={semester} value={semester}>{semester}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Clear Filters */}
            {(searchTerm || sessionFilter || semesterFilter) && (
              <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setSessionFilter('');
                    setSemesterFilter('');
                  }}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#6b7280',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                  }}
                >
                  Clear Filters
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Results Count */}
        <div style={{ marginBottom: '16px', color: '#6b7280', fontSize: '0.875rem' }}>
          Showing {filteredResults.length} of {results.length} results
        </div>

        {/* Results Table */}
        <ResultsTable results={filteredResults} loading={loading} />
      </div>
    </DashboardLayout>
  );
}

export default StudentResults;
