import { theme } from '../../shared/config/theme';
import { ThemeProvider as MuiThemeProvider, CssBaseline } from '@mui/material';

export const ThemeProvider = ({ children }) => {
  return (
    <MuiThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </MuiThemeProvider>
  );
}; 