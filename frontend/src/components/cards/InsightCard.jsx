import React from 'react';
import { motion } from 'framer-motion';

export const InsightCard = ({ title, icon: Icon, children, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay }}
      className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 h-full flex flex-col"
    >
      <div className="flex items-center gap-3 mb-4 pb-3 border-b border-gray-100 dark:border-gray-700">
        {Icon && <Icon className="w-5 h-5 text-blue-500" />}
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
      </div>
      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar text-gray-600 dark:text-gray-300">
        {children}
      </div>
    </motion.div>
  );
};
