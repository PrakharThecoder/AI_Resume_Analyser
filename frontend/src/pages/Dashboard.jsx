import React, { useEffect, useState, useRef } from 'react';
import { Download, Share2, Target, CheckCircle2, AlertCircle, TrendingUp } from 'lucide-react';
import html2pdf from 'html2pdf.js';
import { dashboardService } from '../services/api';
import toast from 'react-hot-toast';
import { KPICard } from '../components/cards/KPICard';
import { InsightCard } from '../components/cards/InsightCard';
import { ATSGaugeChart } from '../components/charts/ATSGaugeChart';
import { SkillMatchPieChart } from '../components/charts/SkillMatchPieChart';
import { ResumeSectionChart } from '../components/charts/ResumeSectionChart';
import { Loader } from '../components/ui/Loader';
import { ErrorState } from '../components/ui/ErrorState';
import { Sidebar } from '../components/dashboard/Sidebar';

export const Dashboard = () => {
  const [data, setData] = useState({
    base_ats_score: 0,
    ats_score: null,
    skill_match_percentage: 0,
    matched_skills: [],
    missing_skills: [],
    section_scores: {},
    candidate_summary: "",
    strengths: [],
    weaknesses: [],
    recommendations: [],
    interview_tips: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const dashboardRef = useRef(null);

  useEffect(() => {
    // Check initial dark mode preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    }
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const analytics = await dashboardService.getAnalytics();

      if (import.meta.env.DEV) {
        console.log("Analytics Response:", analytics);
      }
      setData({
        base_ats_score: analytics?.base_ats_score || 0,
        ats_score: analytics?.ats_score !== undefined ? analytics.ats_score : null,
        skill_match_percentage: analytics?.skill_match_percentage || 0,
        matched_skills: analytics?.matched_skills || [],
        missing_skills: analytics?.missing_skills || [],
        section_scores: analytics?.section_scores || {},
        candidate_summary: analytics?.candidate_summary || "",
        strengths: analytics?.strengths || [],
        weaknesses: analytics?.weaknesses || [],
        recommendations: analytics?.recommendations || [],
        interview_tips: analytics?.interview_tips || [],
      });
    } catch (err) {
      setError(err.message);
      toast.error('Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  const exportPDF = () => {
    const element = dashboardRef.current;
    const opt = {
      margin: 0.5,
      filename: 'ATS_Analytics_Report.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
  };

  if (loading) {
    return <div className="flex h-screen bg-gray-50 dark:bg-gray-950 items-center justify-center"><Loader /></div>;
  }

  if (error) {
    return <div className="flex h-screen bg-gray-50 dark:bg-gray-950 items-center justify-center p-4"><ErrorState message={error} onRetry={fetchData} /></div>;
  }

  if (!data) return null;

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 font-sans transition-colors duration-200">
      <Sidebar isDarkMode={isDarkMode} toggleDarkMode={toggleDarkMode} />

      <main className="flex-1 overflow-y-auto" ref={dashboardRef}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Candidate Analytics
              </h1>
              <p className="text-gray-500 dark:text-gray-400 mt-1">
                Comprehensive evaluation of your resume's quality and job match capabilities.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button onClick={exportPDF} className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm">
                <Download className="w-4 h-4" />
                Export PDF
              </button>
            </div>
          </div>

          {/* KPI Cards Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
            <KPICard
              title="Base ATS Score"
              value={data.base_ats_score}
              icon={Target}
              colorClass={data.base_ats_score >= 71 ? 'text-green-500' : data.base_ats_score >= 41 ? 'text-yellow-500' : 'text-red-500'}
              delay={0.1}
            />
            <KPICard
              title="Job Match Score"
              value={data.ats_score !== null ? data.ats_score : "N/A"}
              icon={Target}
              colorClass={data.ats_score !== null ? (data.ats_score >= 71 ? 'text-green-500' : data.ats_score >= 41 ? 'text-yellow-500' : 'text-red-500') : 'text-gray-400'}
              delay={0.15}
            />
            <KPICard
              title="Skill Match"
              value={`${data.skill_match_percentage}%`}
              icon={TrendingUp}
              colorClass="text-blue-500"
              delay={0.2}
            >
              <div className="mt-4 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-1000"
                  style={{ width: `${data.skill_match_percentage}%` }}
                />
              </div>
            </KPICard>
            <KPICard
              title="Matched Skills"
              value={data?.matched_skills?.length || 0}
              icon={CheckCircle2}
              colorClass="text-emerald-500"
              delay={0.3}
            >
              <div className="mt-4 flex flex-wrap gap-2">
                {Array.isArray(data?.matched_skills) && data.matched_skills.slice(0, 3).map((skill, index) => (
                  <span key={`${skill}-${index}`} className="px-2 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 rounded-md">
                    {skill}
                  </span>
                ))}
                {(data?.matched_skills?.length || 0) > 3 && (
                  <span className="px-2 py-1 text-xs font-medium text-gray-500 dark:text-gray-400">
                    +{(data?.matched_skills?.length || 0) - 3} more
                  </span>
                )}
              </div>
            </KPICard>
            <KPICard
              title="Missing Skills"
              value={data?.missing_skills?.length || 0}
              icon={AlertCircle}
              colorClass="text-red-500"
              delay={0.4}
            >
              <div className="mt-4 flex flex-wrap gap-2">
                {Array.isArray(data?.missing_skills) && data.missing_skills.slice(0, 3).map((skill, index) => (
                  <span key={`${skill}-${index}`} className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 rounded-md">
                    {skill}
                  </span>
                ))}
                {(data?.missing_skills?.length || 0) > 3 && (
                  <span className="px-2 py-1 text-xs font-medium text-gray-500 dark:text-gray-400">
                    +{(data?.missing_skills?.length || 0) - 3} more
                  </span>
                )}
              </div>
            </KPICard>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 lg:col-span-1">
              <h3 className="text-lg font-semibold mb-6">ATS Performance Meter</h3>
              <ATSGaugeChart score={data.ats_score !== null ? data.ats_score : data.base_ats_score} />
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 lg:col-span-1">
              <h3 className="text-lg font-semibold mb-6">Skill Match Distribution</h3>
              <SkillMatchPieChart matchPercentage={data.skill_match_percentage} />
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 lg:col-span-1">
              <h3 className="text-lg font-semibold mb-6">Resume Section Analysis</h3>
              <ResumeSectionChart data={data.section_scores} />
            </div>
          </div>

          {/* Insights Panel */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="lg:col-span-2">
              <InsightCard title="Candidate Summary" delay={0.5}>
                <p className="leading-relaxed">{data.candidate_summary}</p>
              </InsightCard>
            </div>

            <InsightCard title="Missing Skills & Requirements" delay={0.6}>
              <div className="flex flex-wrap gap-2">
                {Array.isArray(data?.missing_skills) && data.missing_skills.map((skill, i) => (
                  <div key={i} className="px-3 py-1.5 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-full text-sm font-medium border border-red-100 dark:border-red-900/50">
                    {skill}
                  </div>
                ))}
                {(!data?.missing_skills || data.missing_skills.length === 0) && (
                  <span className="text-gray-500 text-sm">No missing skills found.</span>
                )}
              </div>
            </InsightCard>

            <InsightCard title="Key Strengths" delay={0.7}>
              <ul className="space-y-3">
                {Array.isArray(data?.strengths) && data.strengths.map((item, i) => (
                  <li key={i} className="flex gap-3 items-start">
                    <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
                {(!data?.strengths || data.strengths.length === 0) && (
                  <li className="text-gray-500 text-sm">No specific strengths identified.</li>
                )}
              </ul>
            </InsightCard>
            
            <InsightCard title="Major Weaknesses" delay={0.75}>
              <ul className="space-y-3">
                {Array.isArray(data?.weaknesses) && data.weaknesses.map((item, i) => (
                  <li key={i} className="flex gap-3 items-start">
                    <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
                {(!data?.weaknesses || data.weaknesses.length === 0) && (
                  <li className="text-gray-500 text-sm">No major weaknesses detected.</li>
                )}
              </ul>
            </InsightCard>

            <InsightCard title="Improvement Recommendations" delay={0.8}>
              <ul className="space-y-3">
                {Array.isArray(data?.recommendations) && data.recommendations.map((item, i) => (
                  <li key={i} className="flex gap-3 items-start">
                    <div className="w-5 h-5 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold">
                      {i + 1}
                    </div>
                    <span>{item}</span>
                  </li>
                ))}
                {(!data?.recommendations || data.recommendations.length === 0) && (
                  <li className="text-gray-500 text-sm">No critical recommendations needed.</li>
                )}
              </ul>
            </InsightCard>

            <div className="lg:col-span-2">
              <InsightCard title="Interview Preparation Tips" delay={0.85}>
                <ul className="space-y-3">
                  {Array.isArray(data?.interview_tips) && data.interview_tips.map((item, i) => (
                    <li key={i} className="flex gap-3 items-start">
                      <TrendingUp className="w-5 h-5 text-indigo-500 shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                  {(!data?.interview_tips || data.interview_tips.length === 0) && (
                    <li className="text-gray-500 text-sm">No specific interview tips generated.</li>
                  )}
                </ul>
              </InsightCard>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
};
