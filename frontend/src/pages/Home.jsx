import React from 'react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="text-center py-24 px-4 sm:px-6 lg:px-8">
      <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 tracking-tight mb-8">
        Optimize Your Resume with <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">AI</span>
      </h1>
      <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
        Upload your resume and the target job description. Our advanced AI powered by local models will analyze your ATS compatibility and provide actionable feedback to help you land the interview.
      </p>
      <div className="flex justify-center gap-4">
        <Link to="/register" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-10 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
          Start Free Analysis
        </Link>
        <Link to="/login" className="bg-white hover:bg-gray-50 text-blue-600 border border-blue-200 font-bold py-4 px-10 rounded-xl shadow-sm transition-all duration-300">
          Sign In
        </Link>
      </div>
      
      <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center text-xl font-bold mb-6 mx-auto">1</div>
          <h3 className="text-xl font-bold mb-3 text-gray-900">Upload PDF</h3>
          <p className="text-gray-500">Securely upload your resume PDF and paste the job description.</p>
        </div>
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-xl flex items-center justify-center text-xl font-bold mb-6 mx-auto">2</div>
          <h3 className="text-xl font-bold mb-3 text-gray-900">AI Processing</h3>
          <p className="text-gray-500">Local Llama 3.2 extracts keywords and evaluates ATS formatting.</p>
        </div>
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          <div className="w-12 h-12 bg-green-100 text-green-600 rounded-xl flex items-center justify-center text-xl font-bold mb-6 mx-auto">3</div>
          <h3 className="text-xl font-bold mb-3 text-gray-900">Get Actionable Insights</h3>
          <p className="text-gray-500">Receive a comprehensive report with match scores and suggestions.</p>
        </div>
      </div>
    </div>
  );
}
