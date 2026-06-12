import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

export const KPICard = ({ title, value, icon: Icon, colorClass, children, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow relative overflow-hidden group"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{title}</p>
          <h3 className={cn("text-3xl font-bold", colorClass || "text-gray-900 dark:text-white")}>
            {value}
          </h3>
        </div>
        {Icon && (
          <div className={cn("p-3 rounded-lg", "bg-gray-50 dark:bg-gray-700 text-gray-400 group-hover:scale-110 transition-transform")}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
      {children}
    </motion.div>
  );
};
