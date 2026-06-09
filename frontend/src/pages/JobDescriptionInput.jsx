import React, { useState } from 'react';

export default function JobDescriptionInput() {
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const MIN_CHARS = 50;
  const MAX_CHARS = 10000;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (jdText.length < MIN_CHARS || jdText.length > MAX_CHARS) {
      setError(`Job description must be between ${MIN_CHARS} and ${MAX_CHARS} characters.`);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/job-description/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_description: jdText }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to analyze job description');
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-2xl shadow-sm border border-gray-100">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Job Description Analysis</h1>
        <p className="text-gray-500">Paste your job description below to extract key requirements and skills.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="jd-text" className="block text-sm font-medium text-gray-700 mb-2">
            Job Description Text
          </label>
          <textarea
            id="jd-text"
            rows={12}
            className={`w-full p-4 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
              jdText.length > MAX_CHARS ? 'border-red-500' : 'border-gray-200'
            }`}
            placeholder="Paste the full job description here..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
          <div className="flex justify-between mt-2 text-sm">
            <span className={jdText.length < MIN_CHARS || jdText.length > MAX_CHARS ? 'text-red-500' : 'text-gray-500'}>
              {jdText.length} / {MAX_CHARS} characters {jdText.length > 0 && jdText.length < MIN_CHARS && `(minimum ${MIN_CHARS})`}
            </span>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 text-red-700 rounded-xl border border-red-100">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || jdText.length < MIN_CHARS || jdText.length > MAX_CHARS}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 px-6 rounded-xl shadow-sm transition-all flex justify-center items-center"
        >
          {loading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing...
            </span>
          ) : (
            'Analyze Job Description'
          )}
        </button>
      </form>

      {result && (
        <div className="mt-12 space-y-6 animate-fade-in-up">
          <h2 className="text-2xl font-bold text-gray-900 border-b pb-4">Extraction Results</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
              <h3 className="text-sm font-bold text-blue-800 uppercase tracking-wider mb-4">Required Skills</h3>
              {result.required_skills?.length > 0 ? (
                <ul className="space-y-2">
                  {result.required_skills.map((skill, i) => (
                    <li key={i} className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span className="text-gray-700">{skill}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 italic">No required skills identified.</p>
              )}
            </div>

            <div className="bg-indigo-50 rounded-xl p-6 border border-indigo-100">
              <h3 className="text-sm font-bold text-indigo-800 uppercase tracking-wider mb-4">Preferred Skills</h3>
              {result.preferred_skills?.length > 0 ? (
                <ul className="space-y-2">
                  {result.preferred_skills.map((skill, i) => (
                    <li key={i} className="flex items-start">
                      <span className="text-indigo-500 mr-2">•</span>
                      <span className="text-gray-700">{skill}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 italic">No preferred skills identified.</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div className="bg-emerald-50 rounded-xl p-6 border border-emerald-100">
              <h3 className="text-sm font-bold text-emerald-800 uppercase tracking-wider mb-2">Experience Requirements</h3>
              <p className="text-gray-700">{result.experience_requirement || <span className="text-gray-500 italic">Not explicitly stated</span>}</p>
            </div>

            <div className="bg-amber-50 rounded-xl p-6 border border-amber-100">
              <h3 className="text-sm font-bold text-amber-800 uppercase tracking-wider mb-2">Education Requirements</h3>
              <p className="text-gray-700">{result.education_requirement || <span className="text-gray-500 italic">Not explicitly stated</span>}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
