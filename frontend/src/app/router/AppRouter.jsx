import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage, RegisterPage, MainPage } from '../../pages';
import { ColdStartPage } from '../../features/cold-start';
import { PlaylistPage } from '../../features/playlist';
import { useAuth } from '../../features/auth/hooks/useAuth';
import { LoadingSpinner } from '../../shared/ui/atoms';

export const AppRouter = () => {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return <LoadingSpinner centered />;
  }

  const handleColdStartNeeded = () => {
    window.location.href = '/cold-start';
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path="/login" 
          element={user ? <Navigate to="/main" replace /> : <LoginPage />} 
        />
        <Route 
          path="/register" 
          element={user ? <Navigate to="/main" replace /> : <RegisterPage />} 
        />
        <Route 
          path="/cold-start" 
          element={user ? <ColdStartPage /> : <Navigate to="/login" replace />} 
        />
        <Route 
          path="/main" 
          element={
            user ? (
              <MainPage 
                user={user}
                onLogout={logout}
                onNeedsColdStart={handleColdStartNeeded}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/playlist/:id" 
          element={user ? <PlaylistPage /> : <Navigate to="/login" replace />} 
        />
        <Route 
          path="/" 
          element={<Navigate to={user ? "/main" : "/login"} replace />} 
        />
      </Routes>
    </BrowserRouter>
  );
}; 