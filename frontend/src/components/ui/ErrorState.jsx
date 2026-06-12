import React from 'react';
import { AlertCircle, RefreshCcw } from 'lucide-react';

export const ErrorState = ({ message, onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-8">
      <div className="w-16 h-16 bg-red-50 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-6">
        <AlertCircle className="w-8 h-8 text-red-500" />
      </div>
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Analysis Failed</h3>
      <p className="text-gray-500 dark:text-gray-400 text-center max-w-md mb-8">
        {message || "We encountered an error while processing the ATS analytics. Please try again."}
      </p>
      
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          <RefreshCcw className="w-4 h-4" />
          Retry Analysis
        </button>
      )}
    </div>
  );
};
