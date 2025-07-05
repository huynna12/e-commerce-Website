import { BrowserRouter, Navigate, Routes, Route } from 'react-router-dom';
import Register from './pages/Register';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import Home from './pages/Home';
import ItemDetail from './components/ItemDetail';
import Profile from './pages/Profile';
// import Navbar from './components/NavBar';
import ProtectedRoute from './components/ProtectedRoute';
import './index.css';

function Logout() {
  localStorage.clear();
  return <Navigate to="/login" />;
}

function RegisterAndClear() {
  // Clear the old session data
  localStorage.clear();
  return <Register />;
}

function App() {
  return (
    <div className='w-full h-full bg-white'>

    
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            // <ProtectedRoute>
              <Home />
            // </ProtectedRoute>
          }
        />
        <Route
          path="/items/:itemId"
          element={
              <ItemDetail />
          }
        />
        <Route path="/login" element={<Login  />}/>
        <Route path="/logout" element={<Logout  />}/>
        <Route path="/register" element={<RegisterAndClear  />}/>

        {/* If go to any other paths, show NotFound page */}
        <Route path="*" element={<NotFound />}/>
      </Routes>
    </BrowserRouter>
    </div>
  );
}

export default App;