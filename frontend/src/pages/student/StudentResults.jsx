import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import ResultsTable from '../../components/results/ResultsTable';
import studentService from '../../services/studentService';
import api from '../../api/axios';
import './student.css';

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
  const [cgpa,            setCgpa]            = useState(0);
  const [totalCredits,    setTotalCredits]    = useState(0);
  const [totalQualityPoints, setTotalQualityPoints] = useState(0);
  const [sessions,        setSessions]        = useState([]);
  const [semesters,       setSemesters]       = useState(0);

  const fetchResults = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await studentService.getResults();
      const resultsData = res.data || [];
      setResults(resultsData);
      
      // Calculate CGPA from results
      let totalCreditUnits = 0;
      let totalQualityPoints = 0;
      resultsData.forEach(result => {
        if (result.grade_point && result.credit_unit) {
          totalCreditUnits += result.credit_unit;
          totalQualityPoints += result.grade_point * result.credit_unit;
        }
      });
      
      setTotalCredits(totalCreditUnits);
      setTotalQualityPoints(totalQualityPoints);
      setCgpa(totalCreditUnits > 0 ? (totalQualityPoints / totalCreditUnits).toFixed(2) : 0);
      
      // Get unique sessions (by years) that the student has results for
      const uniqueSessions = [...new Set(resultsData.map(r => r.session).filter(Boolean))];
      setSessions(uniqueSessions);
      
      // Semesters = 2x sessions (2 semesters per academic year)
      setSemesters(uniqueSessions.length * 2);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchResults(); }, []);

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

                {semesters}

            </h2>

        </div>

    </div>

</div>

        {/* ================= SUMMARY CARDS ================= */}

<div className="results-summary-grid">

    <div className="results-summary-card">

        <span>Cumulative CGPA</span>

        <h2>{cgpa}</h2>

        <p>5-point scale</p>

    </div>

    <div className="results-summary-card">

        <span>Total Credits</span>

        <h2>{totalCredits}</h2>

        <p>Credit units earned</p>

    </div>

    <div className="results-summary-card">

        <span>Quality Points</span>

        <h2>{totalQualityPoints.toFixed(2)}</h2>

        <p>Total quality points</p>

    </div>

    <div className="results-summary-card">

        <span>Total Results</span>

        <h2>{results.length}</h2>

        <p>Published courses</p>

    </div>

</div>

        <p className="sp-results-count">
          Showing <strong>{results.length}</strong> results
        </p>

        {results.length > 0 ? (
          <ResultsTable results={results} loading={false} />
        ) : (
          <div className="sp-empty">
            <div className="sp-empty-icon"><IconFileText /></div>
            <h3>No results found</h3>
            <p>Your results will appear here once published.</p>
          </div>
        )}

      </div>
    </DashboardLayout>
  );
}

export default StudentResults;
