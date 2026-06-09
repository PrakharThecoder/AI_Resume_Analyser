import React, { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { UploadCloud, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../services/api';

export default function Dashboard() {
  const { user } = useContext(AuthContext);
  const [file, setFile] = useState(null);
  const [jobDesc, setJobDesc] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleAnalyze = async () => {
    if (!file || !jobDesc) return alert("Please provide both a resume (PDF) and a job description.");
    setAnalyzing(true);
    setResults(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const resumeRes = await api.post('/resumes/upload-resume', formData);
      const jobRes = await api.post('/jobs/', { title: "Target Job", description: jobDesc });
      
      const analysisRes = await api.post('/analysis/', {
        resume_id: resumeRes.data.file_id,
        job_id: jobRes.data.id
      });
      
      setResults(analysisRes.data);
    } catch (e) {
      console.error(e);
      alert("Error analyzing resume. Please ensure the backend is running and Ollama model is available.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf' || droppedFile.name.endsWith('.pdf')) {
        setFile(droppedFile);
      } else {
        alert('Please upload a PDF file.');
      }
    }
  };

  return (
    <div className="py-8 max-w-5xl mx-auto">
      <div className="mb-10 text-center">
        <h2 className="text-4xl font-extrabold text-gray-900 mb-4">ATS Analysis Dashboard</h2>
        <p className="text-lg text-gray-500">Discover how well your resume matches the job description.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <h3 className="text-xl font-bold mb-6 flex items-center text-gray-800"><UploadCloud className="mr-3 text-blue-500" /> Upload Resume PDF</h3>
          <div 
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${isDragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input 
              type="file" 
              accept=".pdf"
              onChange={e => setFile(e.target.files[0])}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center w-full h-full">
              <UploadCloud className={`h-12 w-12 mb-3 ${isDragOver ? 'text-blue-500' : 'text-gray-400'}`} />
              <span className="text-sm font-medium text-gray-600 mb-1">{file ? file.name : "Click to select or drag and drop"}</span>
              <span className="text-xs text-gray-400">PDF up to 5MB</span>
            </label>
          </div>
        </div>

        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <h3 className="text-xl font-bold mb-6 flex items-center text-gray-800"><FileText className="mr-3 text-indigo-500" /> Job Description</h3>
          <textarea 
            className="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-gray-700 bg-gray-50"
            rows="6"
            placeholder="Paste the target job description here..."
            value={jobDesc}
            onChange={e => setJobDesc(e.target.value)}
          ></textarea>
        </div>
      </div>

      <div className="mt-10 flex justify-center">
        <button 
          onClick={handleAnalyze}
          disabled={analyzing}
          className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-70 text-white font-bold py-4 px-12 rounded-xl shadow-lg transition-all transform hover:-translate-y-1 flex items-center"
        >
          {analyzing ? (
            <><svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Analyzing with AI...</>
          ) : 'Run ATS Analysis'}
        </button>
      </div>

      {results && (
        <div className="mt-16 bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100">
          <div className="bg-gradient-to-r from-emerald-50 to-teal-50 p-8 border-b border-gray-100 flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-1">Analysis Complete</h3>
              <p className="text-gray-600 text-sm">Review your personalized AI feedback below.</p>
            </div>
            <div className="text-right">
              <div className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1">Match Score</div>
              <div className={`text-5xl font-black ${results.match_score >= 80 ? 'text-green-500' : results.match_score >= 50 ? 'text-yellow-500' : 'text-red-500'}`}>
                {results.match_score}%
              </div>
            </div>
          </div>
          
          <div className="p-8 space-y-8">
            <div>
              <h4 className="text-lg font-bold text-gray-900 mb-3 flex items-center"><CheckCircle className="mr-2 text-green-500 h-5 w-5" /> ATS Feedback</h4>
              <div className="bg-gray-50 p-5 rounded-xl text-gray-700 leading-relaxed border border-gray-100">
                {results.ats_feedback}
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-bold text-gray-900 mb-3 flex items-center"><AlertCircle className="mr-2 text-amber-500 h-5 w-5" /> Detailed AI Report</h4>
              <div className="bg-gray-50 p-5 rounded-xl text-gray-700 leading-relaxed border border-gray-100 whitespace-pre-wrap font-mono text-sm">
                {results.llm_report}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
