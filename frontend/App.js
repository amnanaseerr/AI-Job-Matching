import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [jobs, setJobs] = useState([]);
  const [ranked, setRanked] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:5000/jobs').then(res => setJobs(res.data));
  }, []);

  const matchCandidates = (job_id) => {
    axios.post('http://localhost:5000/match', { job_id }).then(res => setRanked(res.data));
  };

  return (
    <div>
      <h1>NexHire AI Job Matching</h1>
      <h2>Job Listings</h2>
      <ul>
        {jobs.map(job => (
          <li key={job.job_id}>
            {job.job_title} - <button onClick={() => matchCandidates(job.job_id)}>Match Candidates</button>
          </li>
        ))}
      </ul>
      <h2>Ranked Candidates</h2>
      <ul>
        {ranked.map((c, idx) => (
          <li key={idx}>{c.candidate_name} - Score: {c.score.toFixed(2)}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;