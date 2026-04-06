import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Typography,
  Box,
} from '@mui/material';
import type { ComparisonResult, FieldComparison } from '../types';
import { ComparisonStatus } from '../types';

const statusColor = (status: ComparisonStatus) => {
  switch (status) {
    case ComparisonStatus.MATCH:
      return 'success';
    case ComparisonStatus.MISMATCH:
      return 'error';
    case ComparisonStatus.MISSING_IN_PDF:
    case ComparisonStatus.MISSING_IN_DB:
      return 'warning';
    default:
      return 'default';
  }
};

interface Props {
  result: ComparisonResult;
}

export default function ComparisonTable({ result }: Props) {
  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">
          {result.account_number} — {result.document_type}
        </Typography>
        <Box>
          <Chip
            label={result.overall_match ? 'MATCH' : 'MISMATCH'}
            color={result.overall_match ? 'success' : 'error'}
            sx={{ mr: 1 }}
          />
          <Chip label={`Confidence: ${(result.confidence_score * 100).toFixed(0)}%`} variant="outlined" />
        </Box>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Chip label={`Matched: ${result.match_count}`} color="success" size="small" />
        <Chip label={`Mismatched: ${result.mismatch_count}`} color="error" size="small" />
        <Chip label={`Missing: ${result.missing_count}`} color="warning" size="small" />
        <Chip label={`${result.processing_time_ms}ms`} variant="outlined" size="small" />
      </Box>

      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Field</TableCell>
              <TableCell>PDF Value</TableCell>
              <TableCell>DB Value</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Confidence</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {result.field_comparisons.map((fc: FieldComparison, i: number) => (
              <TableRow key={i}>
                <TableCell>{fc.field_name}</TableCell>
                <TableCell>{fc.pdf_value ?? '—'}</TableCell>
                <TableCell>{fc.db_value ?? '—'}</TableCell>
                <TableCell>
                  <Chip
                    label={fc.status}
                    color={statusColor(fc.status) as 'success' | 'error' | 'warning' | 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{(fc.confidence * 100).toFixed(0)}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}
