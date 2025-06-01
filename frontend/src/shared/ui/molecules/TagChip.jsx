import { Chip, Box } from '@mui/material';

export const TagChip = ({ tag, onTagPlay, variant = 'outlined' }) => {
  const handleClick = () => {
    onTagPlay?.(tag);
  };

  return (
    <Chip
      label={tag.name || tag}
      onClick={handleClick}
      variant={variant}
      sx={{
        cursor: 'pointer',
        transition: 'all 0.2s',
        '&:hover': {
          backgroundColor: 'primary.main',
          color: 'primary.contrastText',
          transform: 'scale(1.05)',
        },
      }}
    />
  );
}; 