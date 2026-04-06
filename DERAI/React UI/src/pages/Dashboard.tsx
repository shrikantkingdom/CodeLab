import { useQuery } from '@tanstack/react-query';
import { Box, Typography, Grid, Paper, Chip, Skeleton } from '@mui/material';
import { getHealth } from '../api/deraiApi';

export default function Dashboard() {
  const { data: health, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    refetchInterval: 30000,
  });

  const ServiceStatus = ({ name, status }: { name: string; status?: string }) => (
    <Paper sx={{ p: 2, textAlign: 'center' }}>
      <Typography variant="subtitle1">{name}</Typography>
      {isLoading ? (
        <Skeleton width={80} sx={{ mx: 'auto' }} />
      ) : (
        <Chip
          label={status || 'unknown'}
          color={status === 'connected' || status === 'healthy' ? 'success' : 'warning'}
          sx={{ mt: 1 }}
        />
      )}
    </Paper>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {error && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.light', color: 'error.contrastText' }}>
          <Typography>Backend unavailable: {(error as Error).message}</Typography>
        </Paper>
      )}

      <Grid container spacing={3}>
        <Grid item xs={3}>
          <ServiceStatus name="FastAPI Backend" status={health?.status} />
        </Grid>
        <Grid item xs={3}>
          <ServiceStatus name="Snowflake DB" status={health?.services?.snowflake} />
        </Grid>
        <Grid item xs={3}>
          <ServiceStatus name="DB2" status={health?.services?.db2} />
        </Grid>
        <Grid item xs={3}>
          <ServiceStatus name="Spring Boot" status={health?.services?.springboot} />
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quick Start
        </Typography>
        <Typography variant="body1">
          1. Navigate to <strong>Process</strong> to submit a single document for extraction and comparison.
        </Typography>
        <Typography variant="body1">
          2. View past results in <strong>History</strong>.
        </Typography>
        <Typography variant="body1">
          3. Use the engine selector to choose between PyMuPDF, pdfplumber, Tika, Pegbox, or PDFBox.
        </Typography>
      </Paper>
    </Box>
  );
}
