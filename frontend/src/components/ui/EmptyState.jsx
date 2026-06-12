import React from 'react';
import { FileSearch } from 'lucide-react';

export const EmptyState = ({ onUpload }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full bg-white dark:bg-gray-900 rounded-xl border border-dashed border-gray-300 dark:border-gray-700 p-8">
      <div className="w-20 h-20 bg-gray-50 dark:bg-gray-800 rounded-full flex items-center justify-center mb-6">
        <FileSearch className="w-10 h-10 text-gray-400" />
      </div>
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Analysis Data Found</h3>
      <p className="text-gray-500 dark:text-gray-400 text-center max-w-md mb-8">
        Upload a resume and job description to generate comprehensive ATS analytics.
      </p>
      
      {onUpload && (
        <button
          onClick={onUpload}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors shadow-sm"
        >
          Start New Analysis
        </button>
      )}
    </div>
  );
};
