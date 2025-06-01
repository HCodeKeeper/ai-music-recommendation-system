import { ThemeProvider } from './providers/ThemeProvider';
import { AppRouter } from './router/AppRouter';

export const App = () => {
  return (
    <ThemeProvider>
      <AppRouter />
    </ThemeProvider>
  );
}; 