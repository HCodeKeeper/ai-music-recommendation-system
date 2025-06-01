import { TextField } from '@mui/material';

export const Input = ({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  disabled = false,
  required = false,
  fullWidth = true,
  margin = 'normal',
  error = false,
  helperText,
  ...props
}) => {
  return (
    <TextField
      label={label}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      required={required}
      fullWidth={fullWidth}
      margin={margin}
      error={error}
      helperText={helperText}
      {...props}
    />
  );
}; 