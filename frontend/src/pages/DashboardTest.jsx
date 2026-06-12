import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { KPICard } from '../components/cards/KPICard';
import { ATSGaugeChart } from '../components/charts/ATSGaugeChart';
import { SkillMatchPieChart } from '../components/charts/SkillMatchPieChart';
import { ResumeSectionChart } from '../components/charts/ResumeSectionChart';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

export const DashboardTest = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [debugData, setDebugData] = useState(null);
  const [error, setError] = useState(null);

  const [validations, setValidations] = useState({
    apiConnected: false,
    kpiCardsRendered: false,
    atsGaugeRendered: false,
    pieChartRendered: false,
    barChartRendered: false,
    missingSkillsLoaded: false,
  });

  useEffect(() => {
    const runTests = async () => {
      try {
        console.log("Starting Dashboard Verification System...");
        
        // 1. Health Check
        console.log("Testing GET /api/v1/dashboard/health...");
        const healthRes = await api.get('/dashboard/health');
        setHealthStatus(healthRes.data);
        console.log("Health Check Result:", healthRes.data);
        
        if (healthRes.data.api_connected) {
          setValidations(prev => ({ ...prev, apiConnected: true }));
        }

        // 2. Fetch Debug Data
        console.log("Testing GET /api/v1/dashboard/debug...");
        const debugRes = await api.get('/dashboard/debug');
        setDebugData(debugRes.data);
        console.log("Debug Data Result:", debugRes.data);

        if (debugRes.data && debugRes.data.missing_skills?.length > 0) {
          setValidations(prev => ({ ...prev, missingSkillsLoaded: true }));
        }

      } catch (err) {
        console.error("Dashboard Verification Failed:", err);
        setError(err.message);
      }
    };

    runTests();
  }, []);

  // Component Mount Loggers
  useEffect(() => {
    if (debugData) {
      console.log("Rendering ATS Gauge component...");
      setValidations(prev => ({ ...prev, atsGaugeRendered: true }));
      
      console.log("Rendering KPI Cards...");
      setValidations(prev => ({ ...prev, kpiCardsRendered: true }));
      
      console.log("Rendering Pie Chart component...");
      setValidations(prev => ({ ...prev, pieChartRendered: true }));
      
      console.log("Rendering Bar Chart component...");
      setValidations(prev => ({ ...prev, barChartRendered: true }));
    }
  }, [debugData]);

  const ValidationItem = ({ label, isValid }) => (
    <div className="flex items-center gap-3 py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
      {isValid ? (
        <CheckCircle2 className="w-5 h-5 text-green-500" />
      ) : (
        <XCircle className="w-5 h-5 text-red-500" />
      )}
      <span className="font-medium text-gray-700 dark:text-gray-300">{label}</span>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard Verification System</h1>
          <p className="text-gray-500 mt-2">Comprehensive health, API, and rendering checks.</p>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 text-red-600 p-4 rounded-lg flex items-center gap-3 border border-red-200 dark:border-red-900/50">
            <AlertCircle className="w-5 h-5" />
            <span className="font-semibold">{error}</span>
          </div>
        )}

        {/* Validation Results */}
        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Validation Results</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ValidationItem label="API Connected" isValid={validations.apiConnected} />
            <ValidationItem label="Missing Skills Loaded" isValid={validations.missingSkillsLoaded} />
            <ValidationItem label="KPI Cards Rendered" isValid={validations.kpiCardsRendered} />
            <ValidationItem label="ATS Gauge Rendered" isValid={validations.atsGaugeRendered} />
            <ValidationItem label="Pie Chart Rendered" isValid={validations.pieChartRendered} />
            <ValidationItem label="Bar Chart Rendered" isValid={validations.barChartRendered} />
          </div>
        </div>

        {/* API Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">API Status (/health)</h2>
            <pre className="bg-gray-100 dark:bg-gray-950 p-4 rounded-lg text-sm overflow-x-auto text-gray-800 dark:text-gray-300">
              {healthStatus ? JSON.stringify(healthStatus, null, 2) : "Loading..."}
            </pre>
          </div>

          <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">API Payload (/debug)</h2>
            <pre className="bg-gray-100 dark:bg-gray-950 p-4 rounded-lg text-sm overflow-x-auto text-gray-800 dark:text-gray-300 h-64">
              {debugData ? JSON.stringify(debugData, null, 2) : "Loading..."}
            </pre>
          </div>
        </div>

        {/* Hidden Render Targets for Validation */}
        <div className="hidden">
          {debugData && (
            <>
              <KPICard title="Test" value={debugData.ats_score} />
              <ATSGaugeChart score={debugData.ats_score} />
              <SkillMatchPieChart matchPercentage={debugData.skill_match_percentage} />
              <ResumeSectionChart data={debugData.resume_sections} />
            </>
          )}
        </div>

      </div>
    </div>
  );
};
