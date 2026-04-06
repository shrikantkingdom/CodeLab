import { useState } from 'react';
import {
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Grid,
  Paper,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  DocumentType,
  StatementType,
  LetterType,
  ConfirmType,
  ProductType,
  ExtractionEngine,
} from '../types';
import type { ProcessSingleRequest } from '../types';

interface Props {
  onSubmit: (request: ProcessSingleRequest) => void;
  loading?: boolean;
  error?: string | null;
}

export default function SingleInputForm({ onSubmit, loading = false, error = null }: Props) {
  const [office, setOffice] = useState('');
  const [account, setAccount] = useState('');
  const [docType, setDocType] = useState<DocumentType>(DocumentType.STATEMENT);
  const [engine, setEngine] = useState<ExtractionEngine>(ExtractionEngine.PYMUPDF);

  // Statement fields
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [statementType, setStatementType] = useState<StatementType>(StatementType.MONTHLY);
  const [productType, setProductType] = useState<ProductType>(ProductType.ALL);

  // Letter fields
  const [letterType, setLetterType] = useState<LetterType>(LetterType.WELCOME);
  const [loadDate, setLoadDate] = useState('');

  // Confirm fields
  const [confirmType, setConfirmType] = useState<ConfirmType>(ConfirmType.TRADE);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const request: ProcessSingleRequest = {
      account_number: { office, account },
      document_type: docType,
      extraction_engine: engine,
    };

    if (docType === DocumentType.STATEMENT) {
      request.statement_input = {
        start_date: startDate,
        end_date: endDate,
        statement_type: statementType,
        product_type: productType,
      };
    } else if (docType === DocumentType.LETTER) {
      request.letter_input = {
        letter_type: letterType,
        load_date: loadDate,
      };
    } else {
      request.confirm_input = {
        start_date: startDate,
        end_date: endDate,
        confirm_type: confirmType,
        product_type: productType,
      };
    }

    onSubmit(request);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Process Single Document
      </Typography>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          {/* Account */}
          <Grid item xs={3}>
            <TextField
              label="Office"
              value={office}
              onChange={(e) => setOffice(e.target.value)}
              required
              fullWidth
              inputProps={{ maxLength: 3 }}
            />
          </Grid>
          <Grid item xs={3}>
            <TextField
              label="Account"
              value={account}
              onChange={(e) => setAccount(e.target.value)}
              required
              fullWidth
              inputProps={{ maxLength: 6 }}
            />
          </Grid>

          {/* Document Type */}
          <Grid item xs={3}>
            <FormControl fullWidth>
              <InputLabel>Document Type</InputLabel>
              <Select
                value={docType}
                label="Document Type"
                onChange={(e) => setDocType(e.target.value as DocumentType)}
              >
                {Object.values(DocumentType).map((dt) => (
                  <MenuItem key={dt} value={dt}>
                    {dt}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Engine */}
          <Grid item xs={3}>
            <FormControl fullWidth>
              <InputLabel>Engine</InputLabel>
              <Select
                value={engine}
                label="Engine"
                onChange={(e) => setEngine(e.target.value as ExtractionEngine)}
              >
                {Object.values(ExtractionEngine).map((eng) => (
                  <MenuItem key={eng} value={eng}>
                    {eng}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Conditional fields based on document type */}
          {(docType === DocumentType.STATEMENT || docType === DocumentType.CONFIRM) && (
            <>
              <Grid item xs={3}>
                <TextField
                  label="Start Date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  required
                  fullWidth
                />
              </Grid>
              <Grid item xs={3}>
                <TextField
                  label="End Date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  required
                  fullWidth
                />
              </Grid>
              <Grid item xs={3}>
                <FormControl fullWidth>
                  <InputLabel>Product</InputLabel>
                  <Select
                    value={productType}
                    label="Product"
                    onChange={(e) => setProductType(e.target.value as ProductType)}
                  >
                    {Object.values(ProductType).map((p) => (
                      <MenuItem key={p} value={p}>
                        {p}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </>
          )}

          {docType === DocumentType.STATEMENT && (
            <Grid item xs={3}>
              <FormControl fullWidth>
                <InputLabel>Statement Type</InputLabel>
                <Select
                  value={statementType}
                  label="Statement Type"
                  onChange={(e) => setStatementType(e.target.value as StatementType)}
                >
                  {Object.values(StatementType).map((st) => (
                    <MenuItem key={st} value={st}>
                      {st}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          )}

          {docType === DocumentType.CONFIRM && (
            <Grid item xs={3}>
              <FormControl fullWidth>
                <InputLabel>Confirm Type</InputLabel>
                <Select
                  value={confirmType}
                  label="Confirm Type"
                  onChange={(e) => setConfirmType(e.target.value as ConfirmType)}
                >
                  {Object.values(ConfirmType).map((ct) => (
                    <MenuItem key={ct} value={ct}>
                      {ct}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          )}

          {docType === DocumentType.LETTER && (
            <>
              <Grid item xs={3}>
                <FormControl fullWidth>
                  <InputLabel>Letter Type</InputLabel>
                  <Select
                    value={letterType}
                    label="Letter Type"
                    onChange={(e) => setLetterType(e.target.value as LetterType)}
                  >
                    {Object.values(LetterType).map((lt) => (
                      <MenuItem key={lt} value={lt}>
                        {lt}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={3}>
                <TextField
                  label="Load Date"
                  type="date"
                  value={loadDate}
                  onChange={(e) => setLoadDate(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  required
                  fullWidth
                />
              </Grid>
            </>
          )}

          <Grid item xs={12}>
            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? <CircularProgress size={24} /> : 'Process'}
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
}
