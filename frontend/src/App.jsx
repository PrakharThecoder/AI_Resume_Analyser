import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import JobDescriptionInput from './pages/JobDescriptionInput';
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col bg-gray-50">
          <nav className="bg-white shadow-sm border-b p-4 sticky top-0 z-10">
            <div className="max-w-7xl mx-auto flex justify-between items-center">
              <Link to="/" className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                ResumeAI
              </Link>
              <div className="space-x-4">
                <Link to="/login" className="text-gray-600 hover:text-blue-600 font-medium transition-colors">Login</Link>
                <Link to="/register" className="bg-blue-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-blue-700 shadow-md transition-all">Get Started</Link>
              </div>
            </div>
          </nav>
          
          <main className="flex-grow max-w-7xl mx-auto w-full p-4 md:p-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/jd-input" element={<JobDescriptionInput />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
