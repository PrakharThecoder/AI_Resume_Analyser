import React from 'react';
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts';

export const ATSGaugeChart = ({ score }) => {
  const data = [
    {
      name: 'Score',
      value: score,
      fill: score >= 71 ? '#10B981' : score >= 41 ? '#F59E0B' : '#EF4444',
    }
  ];

  return (
    <div className="h-[300px] w-full relative flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart 
          cx="50%" 
          cy="50%" 
          innerRadius="70%" 
          outerRadius="100%" 
          barSize={20} 
          data={data}
          startAngle={180}
          endAngle={0}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar
            minAngle={15}
            background={{ fill: '#E5E7EB' }}
            clockWise
            dataKey="value"
            cornerRadius={10}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      
      {/* Center Label */}
      <div className="absolute inset-0 flex flex-col items-center justify-center mt-12">
        <span className="text-5xl font-bold text-gray-900 dark:text-white">{score}</span>
        <span className="text-sm font-medium text-gray-500 uppercase tracking-wider mt-1">ATS Score</span>
      </div>
    </div>
  );
};
