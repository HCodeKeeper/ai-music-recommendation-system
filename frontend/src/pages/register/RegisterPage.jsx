import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Alert } from '@mui/material';
import { Button, Input, LoadingSpinner } from '../../shared/ui/atoms';
import { useAuth } from '../../features/auth/hooks/useAuth';
import { t } from '../../shared/lib/translations';

export const RegisterPage = () => {
  const [form, setForm] = useState({ email: '', password: '', name: '' });
  const [error, setError] = useState('');
  const { register, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!form.email || !form.password || !form.name) {
      setError(t('fillAllFields'));
      return;
    }

    setError('');
    const result = await register(form.email, form.password, form.name);
    
    if (result.success) {
      navigate('/cold-start');
    } else {
      setError(result.error);
    }
  };

  return (
    <Box sx={{ 
      height: '100vh',
      width: '100vw',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <Box sx={{ width: '100%', maxWidth: 400, p: 3 }}>
        <Typography variant="h4" gutterBottom align="center">
          {t('signUp')}
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={handleSubmit}>
          <Input
            label={t('name')}
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            disabled={loading}
            required
          />
          <Input
            label={t('email')}
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            disabled={loading}
            required
          />
          <Input
            label={t('password')}
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            disabled={loading}
            required
          />
          
          <Button
            type="submit"
            fullWidth
            disabled={loading}
            sx={{ mt: 3, mb: 2 }}
          >
            {loading ? <LoadingSpinner size={24} /> : t('signUp')}
          </Button>
        </Box>
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2">
            {t('alreadyHaveAccount')}{' '}
            <Button
              variant="text"
              onClick={() => navigate('/login')}
              disabled={loading}
            >
              {t('login')}
            </Button>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}; 