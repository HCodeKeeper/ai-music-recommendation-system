import { Button as MuiButton } from '@mui/material';

export const Button = ({ 
  children, 
  variant = 'contained',
  color = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  startIcon,
  endIcon,
  onClick,
  type = 'button',
  fullWidth = false,
  ...props 
}) => {
  return (
    <MuiButton
      variant={variant}
      color={color}
      size={size}
      disabled={disabled || loading}
      startIcon={loading ? undefined : startIcon}
      endIcon={endIcon}
      onClick={onClick}
      type={type}
      fullWidth={fullWidth}
      {...props}
    >
      {children}
    </MuiButton>
  );
}; 