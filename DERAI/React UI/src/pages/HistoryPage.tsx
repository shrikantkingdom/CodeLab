import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Box, Typography, TextField, Button, Paper, CircularProgress } from '@mui/material';
import ComparisonTable from '../components/ComparisonTable';
import { getCompareResults } from '../api/deraiApi';

export default function HistoryPage() {
  const [filter, setFilter] = useState('');
  const [searchAccount, setSearchAccount] = useState<string | undefined>(undefined);

  const { data: results, isLoading } = useQuery({
    queryKey: ['compare-results', searchAccount],
    queryFn: () => getCompareResults(searchAccount, 50),
  });

  const handleSearch = () => {
    setSearchAccount(filter || undefined);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Comparison History
      </Typography>

      <Paper sx={{ p: 2, mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
        <TextField
          label="Filter by Account Number"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          size="small"
          placeholder="e.g. 001-123456"
        />
        <Button variant="contained" onClick={handleSearch}>
          Search
        </Button>
        <Button
          variant="outlined"
          onClick={() => {
            setFilter('');
            setSearchAccount(undefined);
          }}
        >
          Clear
        </Button>
      </Paper>

      {isLoading && <CircularProgress />}

      {results && results.length === 0 && (
        <Typography color="text.secondary">No results found.</Typography>
      )}

      {results?.map((result, i) => (
        <ComparisonTable key={i} result={result} />
      ))}
    </Box>
  );
}
