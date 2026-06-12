import React from 'react';
import { Loader2 } from 'lucide-react';

export const Loader = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full">
      <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
      <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300">Analyzing ATS Data...</h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 text-center max-w-sm">
        Please wait while we process the resume and job description against our algorithms.
      </p>
    </div>
  );
};

export const Skeleton = ({ className }) => (
  <div className={`animate-pulse bg-gray-200 dark:bg-gray-800 rounded-lg ${className}`} />
);
