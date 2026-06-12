import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { DashboardTest } from './pages/DashboardTest';
import JobDescriptionInput from './pages/JobDescriptionInput';

const AppLayout = ({ children }) => {
  const location = useLocation();
  const isDashboard = location.pathname.startsWith('/dashboard');

  if (isDashboard) {
    return children;
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors">
      <nav className="bg-white dark:bg-gray-800 shadow-sm border-b dark:border-gray-700 p-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link to="/" className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
            ResumeAI
          </Link>
          <div className="space-x-4">
            <Link to="/login" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 font-medium transition-colors">Login</Link>
            <Link to="/register" className="bg-blue-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-blue-700 shadow-md transition-all">Get Started</Link>
          </div>
        </div>
      </nav>
      
      <main className="flex-grow max-w-7xl mx-auto w-full p-4 md:p-8">
        {children}
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard/test" element={<DashboardTest />} />
            <Route path="/dashboard/*" element={<Dashboard />} />
            <Route path="/jd-input" element={<JobDescriptionInput />} />
          </Routes>
        </AppLayout>
      </Router>
    </AuthProvider>
  );
}

export default App;
