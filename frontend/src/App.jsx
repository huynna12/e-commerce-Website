import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Register from './pages/Register';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import Home from './pages/Home';
import Profile from './pages/Profile';
import ItemDetail from './pages/ItemDetail';
import './index.css';

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
            path="heidi/"
            element={
              // <ProtectedRoute>
                <Home />
              // </ProtectedRoute>
            }
          />
           <Route
            path="/heidi/"
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
          <Route path="/register" element={<RegisterAndClear  />}/>
          <Route path="/profile/:username" element={<Profile />} />
          {/* If go to any other paths, show NotFound page */}
          <Route path="*" element={<NotFound />}/>
      </Routes>
    </BrowserRouter>
    </div>
  );
}

export default App;