import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import ResultsTable from '../../components/results/ResultsTable';
import studentService from '../../services/studentService';
import './student.css';

const IconSearch = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
  </svg>
);

const IconFileText = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
  </svg>
);

const IconAlertCircle = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
    <line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
);

function StudentResults() {
  const [results,         setResults]         = useState([]);
  const [loading,         setLoading]         = useState(true);
  const [error,           setError]           = useState(null);
  const [searchTerm,      setSearchTerm]      = useState('');
  const [sessionFilter,   setSessionFilter]   = useState('');
  const [semesterFilter,  setSemesterFilter]  = useState('');

  const fetchResults = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await studentService.getResults();
      setResults(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchResults(); }, []);

  const sessions  = [...new Set(results.map(r => r.session).filter(Boolean))];
  const semesters = [...new Set(results.map(r => r.semester).filter(Boolean))];

  const filtered = results.filter(r => {
    const q = searchTerm.toLowerCase();
    const matchSearch   = !q || r.course_code?.toLowerCase().includes(q) || r.course_title?.toLowerCase().includes(q);
    const matchSession  = !sessionFilter  || r.session  === sessionFilter;
    const matchSemester = !semesterFilter || r.semester === semesterFilter;
    return matchSearch && matchSession && matchSemester;
  });

  const hasFilters = searchTerm || sessionFilter || semesterFilter;
  const clearFilters = () => { setSearchTerm(''); setSessionFilter(''); setSemesterFilter(''); };

  if (loading) return (
    <DashboardLayout userRole="student">
      <div className="sp-page">
        <div className="sp-skeleton" style={{ height: 36, width: 200, marginBottom: 24, borderRadius: 8 }} />
        <div className="sp-skeleton" style={{ height: 80, borderRadius: 14, marginBottom: 20 }} />
        <div className="sp-skeleton" style={{ height: 300, borderRadius: 14 }} />
      </div>
    </DashboardLayout>
  );

  if (error) return (
    <DashboardLayout userRole="student">
      <div className="sp-empty" style={{ marginTop: 40 }}>
        <div className="sp-empty-icon" style={{ background: 'var(--red-light)', color: 'var(--red)' }}>
          <IconAlertCircle />
        </div>
        <h3>Couldn't load results</h3>
        <p>{error}</p>
        <button className="sp-filter-clear" style={{ marginTop: 16 }} onClick={fetchResults}>Retry</button>
      </div>
    </DashboardLayout>
  );

  return (
    <DashboardLayout userRole="student">
      <div className="sp-page">

        {/* ================= RESULTS HERO ================= */}

<div className="results-hero">

    <div className="results-hero-left">

        <span className="results-eyebrow">

            📊 Student Hub

        </span>

        <h1>

            Results Hub

        </h1>

        <p>

            Explore your academic performance across every
            semester and session. Track your progress,
            identify strengths and monitor your achievements.

        </p>

    </div>

    <div className="results-hero-right">

        <div className="results-hero-stat">

            <span>

                Courses

            </span>

            <h2>

                {results.length}

            </h2>

        </div>

        <div className="results-divider"></div>

        <div className="results-hero-stat">

            <span>

                Sessions

            </span>

            <h2>

                {sessions.length}

            </h2>

        </div>

        <div className="results-divider"></div>

        <div className="results-hero-stat">

            <span>

                Semesters

            </span>

            <h2>

                {semesters.length}

            </h2>

        </div>

    </div>

</div>

        {/* ================= SUMMARY CARDS ================= */}

<div className="results-summary-grid">

    <div className="results-summary-card">

        <span>Total Results</span>

        <h2>{results.length}</h2>

        <p>Published courses</p>

    </div>

    <div className="results-summary-card">

        <span>Visible Results</span>

        <h2>{filtered.length}</h2>

        <p>After filtering</p>

    </div>

    <div className="results-summary-card">

        <span>Sessions</span>

        <h2>{sessions.length}</h2>

        <p>Academic sessions</p>

    </div>

    <div className="results-summary-card">

        <span>Semesters</span>

        <h2>{semesters.length}</h2>

        <p>Available semesters</p>

    </div>

</div>

        {/* Filter Bar */}
        <div className="sp-filter-bar">
          <div className="sp-filter-group grow">
            <label className="sp-filter-label">Search</label>
            <input
              className="sp-filter-input"
              type="text"
              placeholder="Course code or title…"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>

          {sessions.length > 0 && (
            <div className="sp-filter-group fixed">
              <label className="sp-filter-label">Session</label>
              <select className="sp-filter-select" value={sessionFilter} onChange={e => setSessionFilter(e.target.value)}>
                <option value="">All Sessions</option>
                {sessions.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          )}

          {semesters.length > 0 && (
            <div className="sp-filter-group fixed">
              <label className="sp-filter-label">Semester</label>
              <select className="sp-filter-select" value={semesterFilter} onChange={e => setSemesterFilter(e.target.value)}>
                <option value="">All Semesters</option>
                {semesters.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          )}

          {hasFilters && (
            <button className="sp-filter-clear" onClick={clearFilters}>Clear filters</button>
          )}
        </div>

        <p className="sp-results-count">
          Showing <strong>{filtered.length}</strong> of <strong>{results.length}</strong> results
        </p>

        {filtered.length > 0 ? (
          <ResultsTable results={filtered} loading={false} />
        ) : (
          <div className="sp-empty">
            <div className="sp-empty-icon"><IconFileText /></div>
            <h3>No results found</h3>
            <p>{hasFilters ? 'Try adjusting your filters.' : 'Your results will appear here once published.'}</p>
          </div>
        )}

      </div>
    </DashboardLayout>
  );
}

export default StudentResults;
