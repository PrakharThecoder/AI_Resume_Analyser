import React, { useState, useEffect, useRef } from 'react';
import { Sidebar } from '../components/dashboard/Sidebar';
import { resumeService } from '../services/api';
import toast from 'react-hot-toast';
import { UploadCloud, FileText, Play, Download, Trash2, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

export const Resumes = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [selectedResumeId, setSelectedResumeId] = useState(null);
  const [selectedRole, setSelectedRole] = useState("Software Engineer");

  const ROLES = [
    "Software Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Data Scientist",
    "Machine Learning Engineer",
    "DevOps Engineer"
  ];
  
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    }
    fetchResumes();
  }, []);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  const fetchResumes = async () => {
    try {
      const data = await resumeService.getResumes();
      // Sort by upload date descending
      const sorted = data.sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date));
      setResumes(sorted);
    } catch (err) {
      toast.error('Failed to load resumes');
    } finally {
      setLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = async (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      await handleUpload(e.target.files[0]);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleUpload = async (file) => {
    if (file.type !== 'application/pdf') {
      toast.error('Only PDF files are allowed');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      await resumeService.uploadResume(file, (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(percentCompleted);
      });
      toast.success('Resume uploaded successfully!');
      fetchResumes();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to upload resume');
    } finally {
      setUploading(false);
      setUploadProgress(0);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this resume?")) return;
    
    try {
      await resumeService.deleteResume(id);
      toast.success("Resume deleted");
      setResumes(resumes.filter(r => r.id !== id));
    } catch (err) {
      toast.error("Failed to delete resume");
    }
  };

  const openRoleModal = (id) => {
    setSelectedResumeId(id);
    setRoleModalOpen(true);
  };

  const handleAnalyzeSubmit = async () => {
    if (!selectedResumeId) return;
    setRoleModalOpen(false);
    const id = selectedResumeId;
    
    // Optimistic UI update
    setResumes(resumes.map(r => r.id === id ? { ...r, analysis_status: 'Analyzing...' } : r));
    
    try {
      const result = await resumeService.analyzeResume(id, selectedRole);
      toast.success("Analysis complete");
      setResumes(resumes.map(r => r.id === id ? { ...r, analysis_status: result.analysis_status, ats_score: result.ats_score } : r));
    } catch (err) {
      toast.error("Analysis failed");
      setResumes(resumes.map(r => r.id === id ? { ...r, analysis_status: 'Failed' } : r));
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 font-sans transition-colors duration-200">
      <Sidebar isDarkMode={isDarkMode} toggleDarkMode={toggleDarkMode} />
      
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
          
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Resume Management
            </h1>
          </div>

          {/* Upload Section */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-8">
            <h2 className="text-xl font-semibold mb-6">Upload New Resume</h2>
            
            <div 
              className={`relative border-2 border-dashed rounded-xl p-10 text-center transition-all ${
                dragActive ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700/50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input 
                ref={fileInputRef}
                type="file" 
                className="hidden" 
                accept="application/pdf"
                onChange={handleChange}
              />
              
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="p-4 bg-blue-100 dark:bg-blue-900/50 rounded-full text-blue-600 dark:text-blue-400">
                  <UploadCloud className="w-8 h-8" />
                </div>
                <div>
                  <p className="text-lg font-medium">
                    Drag and drop your PDF here, or <button onClick={onButtonClick} className="text-blue-600 dark:text-blue-400 font-semibold hover:underline">browse files</button>
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Maximum file size: 5MB</p>
                </div>
              </div>

              {uploading && (
                <div className="absolute inset-0 bg-white/90 dark:bg-gray-800/90 rounded-xl flex flex-col items-center justify-center p-6">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-4" />
                  <div className="w-full max-w-md bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                    <div className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" style={{ width: `${uploadProgress}%` }}></div>
                  </div>
                  <p className="mt-2 text-sm font-medium">Uploading... {uploadProgress}%</p>
                </div>
              )}
            </div>
          </div>

          {/* Table Section */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
            <div className="p-6 border-b border-gray-100 dark:border-gray-700">
              <h2 className="text-xl font-semibold">Your Resumes</h2>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700">
                    <th className="p-4 font-semibold text-sm text-gray-600 dark:text-gray-300">Filename</th>
                    <th className="p-4 font-semibold text-sm text-gray-600 dark:text-gray-300">Upload Date</th>
                    <th className="p-4 font-semibold text-sm text-gray-600 dark:text-gray-300">Status</th>
                    <th className="p-4 font-semibold text-sm text-gray-600 dark:text-gray-300">Base ATS Score</th>
                    <th className="p-4 font-semibold text-sm text-gray-600 dark:text-gray-300 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {loading ? (
                    <tr>
                      <td colSpan="5" className="p-8 text-center">
                        <Loader2 className="w-6 h-6 animate-spin text-blue-600 mx-auto" />
                      </td>
                    </tr>
                  ) : resumes.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="p-12 text-center text-gray-500">
                        <FileText className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
                        <p>No resumes uploaded yet. Upload your first resume above.</p>
                      </td>
                    </tr>
                  ) : (
                    resumes.map((resume) => (
                      <tr key={resume.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <FileText className="w-5 h-5 text-gray-400" />
                            <span className="font-medium truncate max-w-[200px]" title={resume.filename}>
                              {resume.filename}
                            </span>
                          </div>
                        </td>
                        <td className="p-4 text-gray-500 dark:text-gray-400">
                          {new Date(resume.upload_date).toLocaleDateString()}
                        </td>
                        <td className="p-4">
                          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                            resume.analysis_status === 'Completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                            resume.analysis_status === 'Analyzing...' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                            resume.analysis_status === 'Failed' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
                            'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
                          }`}>
                            {resume.analysis_status === 'Completed' && <CheckCircle className="w-3 h-3" />}
                            {resume.analysis_status === 'Analyzing...' && <Loader2 className="w-3 h-3 animate-spin" />}
                            {resume.analysis_status === 'Failed' && <AlertCircle className="w-3 h-3" />}
                            {resume.analysis_status}
                          </span>
                        </td>
                        <td className="p-4 font-semibold">
                          {resume.ats_score !== null ? (
                            <span className={resume.ats_score > 70 ? 'text-green-600 dark:text-green-400' : 'text-amber-600 dark:text-amber-400'}>
                              {resume.ats_score} / 100
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="p-4 text-right space-x-2">
                          <button 
                            onClick={() => openRoleModal(resume.id)}
                            disabled={resume.analysis_status === 'Analyzing...'}
                            className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors disabled:opacity-50"
                            title="Run Baseline Analysis"
                          >
                            <Play className="w-4 h-4" />
                          </button>
                          <a 
                            href={`${import.meta.env.VITE_API_URL.replace('/api/v1', '')}/uploads/resumes/${resume.owner_id}_${resume.filename}`}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-block p-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition-colors"
                            title="Download PDF"
                          >
                            <Download className="w-4 h-4" />
                          </a>
                          <button 
                            onClick={() => handleDelete(resume.id)}
                            className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                            title="Delete Resume"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </main>

      {/* Role Selection Modal */}
      {roleModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md shadow-xl border border-gray-100 dark:border-gray-700">
            <h3 className="text-xl font-bold mb-4">Select Target Role</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Choose the role you want to benchmark this resume against.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Target Role</label>
                <select 
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  {ROLES.map(role => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button 
                  onClick={() => setRoleModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleAnalyzeSubmit}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                >
                  Start Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
