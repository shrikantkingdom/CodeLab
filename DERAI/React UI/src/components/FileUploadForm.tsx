import { useState, useRef, useEffect } from 'react';
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
  Chip,
  ListSubheader,
  Tooltip,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { DocumentType, ExtractionEngine } from '../types';
import type { AIProviderStatus } from '../types';
import { getAIProviders } from '../api/deraiApi';

const TEXT_ENGINES = ['pdfminer', 'pymupdf', 'pdfplumber'] as const;

const isHybridEngine = (engine: ExtractionEngine) =>
  [
    ExtractionEngine.HYBRID_OCR_PYTESSERACT,
    ExtractionEngine.HYBRID_OCR_AZURE,
    ExtractionEngine.OCR_PYTESSERACT,
    ExtractionEngine.OCR_AZURE,
  ].includes(engine);

interface Props {
  onSubmit: (formData: FormData) => void;
  loading?: boolean;
  error?: string | null;
}

export default function FileUploadForm({ onSubmit, loading = false, error = null }: Props) {
  const [office, setOffice] = useState('');
  const [account, setAccount] = useState('');
  const [docType, setDocType] = useState<DocumentType>(DocumentType.STATEMENT);
  const [engine, setEngine] = useState<ExtractionEngine>(ExtractionEngine.PDFMINER);
  const [hybridTextEngine, setHybridTextEngine] = useState<string>('pdfminer');
  const [pageNumbers, setPageNumbers] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [aiProvider, setAiProvider] = useState<string>('openai');
  const [aiModel, setAiModel] = useState<string>('');
  const [providers, setProviders] = useState<AIProviderStatus[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch available AI providers on mount
  useEffect(() => {
    getAIProviders()
      .then((res) => {
        setProviders(res.providers);
        setAiProvider(res.current_provider);
        // Set initial model from the current provider
        const current = res.providers.find(p => p.id === res.current_provider);
        if (current) setAiModel(current.model);
      })
      .catch(() => {
        // fallback if endpoint unavailable
        setProviders([
          { id: 'openai', name: 'OpenAI', configured: false, model: 'gpt-4o', available_models: ['gpt-4o', 'gpt-4o-mini'] },
          { id: 'github_copilot', name: 'GitHub Copilot (Models API)', configured: false, model: 'gpt-4o', available_models: ['gpt-4o', 'gpt-4o-mini'] },
          { id: 'anthropic', name: 'Anthropic Claude', configured: false, model: 'claude-sonnet-4-20250514', available_models: ['claude-sonnet-4-20250514'] },
          { id: 'google_gemini', name: 'Google Gemini', configured: false, model: 'gemini-1.5-pro', available_models: ['gemini-1.5-pro'] },
          { id: 'deepseek', name: 'DeepSeek', configured: false, model: 'deepseek-chat', available_models: ['deepseek-chat', 'deepseek-reasoner'] },
          { id: 'regex_only', name: 'Regex Only (no AI)', configured: true, model: 'regex', available_models: ['regex'] },
        ]);
      });
  }, []);

  // When provider changes, set model to that provider's default
  const handleProviderChange = (newProvider: string) => {
    setAiProvider(newProvider);
    const prov = providers.find(p => p.id === newProvider);
    if (prov) setAiModel(prov.model);
  };

  // Get available models for currently selected provider
  const currentProviderModels = providers.find(p => p.id === aiProvider)?.available_models ?? [];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      if (dropped.type === 'application/pdf' || dropped.name.toLowerCase().endsWith('.pdf')) {
        setFile(dropped);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('office', office);
    formData.append('account', account);
    formData.append('document_type', docType);
    formData.append('extraction_engine', engine);
    if (pageNumbers.trim()) {
      formData.append('page_numbers', pageNumbers.trim());
    }
    if (isHybridEngine(engine)) {
      formData.append('hybrid_text_engine', hybridTextEngine);
    }
    formData.append('ai_provider', aiProvider);
    if (aiModel) {
      formData.append('ai_model', aiModel);
    }

    onSubmit(formData);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Upload &amp; Process Document
      </Typography>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          {/* File Upload Zone */}
          <Grid item xs={12}>
            <Box
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              sx={{
                border: '2px dashed',
                borderColor: dragActive ? 'primary.main' : file ? 'success.main' : 'grey.400',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                bgcolor: dragActive ? 'action.hover' : file ? 'success.light' : 'background.paper',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' },
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              {file ? (
                <Box>
                  <InsertDriveFileIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                  <Typography variant="body1" fontWeight="bold">
                    {file.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {(file.size / 1024).toFixed(1)} KB — Click or drag to replace
                  </Typography>
                </Box>
              ) : (
                <Box>
                  <CloudUploadIcon sx={{ fontSize: 48, color: 'grey.500', mb: 1 }} />
                  <Typography variant="body1">
                    Drag &amp; drop a PDF here, or click to browse
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Only PDF files are accepted
                  </Typography>
                </Box>
              )}
            </Box>
          </Grid>

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
                <ListSubheader>Text Extractors</ListSubheader>
                <MenuItem value={ExtractionEngine.PDFMINER}>pdfminer</MenuItem>
                <MenuItem value={ExtractionEngine.PYMUPDF}>pymupdf</MenuItem>
                <MenuItem value={ExtractionEngine.PDFPLUMBER}>pdfplumber</MenuItem>
                <MenuItem value={ExtractionEngine.TIKA}>tika</MenuItem>
                <ListSubheader>Java (Spring Boot)</ListSubheader>
                <MenuItem value={ExtractionEngine.PEGBOX}>pegbox</MenuItem>
                <MenuItem value={ExtractionEngine.PDFBOX}>pdfbox</MenuItem>
                <ListSubheader>Hybrid OCR (auto-detect image pages)</ListSubheader>
                <MenuItem value={ExtractionEngine.HYBRID_OCR_PYTESSERACT}>hybrid + pytesseract</MenuItem>
                <MenuItem value={ExtractionEngine.HYBRID_OCR_AZURE}>hybrid + azure</MenuItem>
                <ListSubheader>Full OCR (all pages)</ListSubheader>
                <MenuItem value={ExtractionEngine.OCR_PYTESSERACT}>ocr pytesseract</MenuItem>
                <MenuItem value={ExtractionEngine.OCR_AZURE}>ocr azure</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* AI Provider */}
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>AI Provider</InputLabel>
              <Select
                value={aiProvider}
                label="AI Provider"
                onChange={(e) => handleProviderChange(e.target.value)}
              >
                {providers.map((p) => (
                  <MenuItem key={p.id} value={p.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                      <Tooltip title={p.configured ? `Configured — model: ${p.model}` : 'API key not set'}>
                        {p.configured
                          ? <CheckCircleIcon fontSize="small" color="success" />
                          : <CancelIcon fontSize="small" color="disabled" />
                        }
                      </Tooltip>
                      <span>{p.name}</span>
                      <Chip label={`${p.available_models.length} models`} size="small" variant="outlined" sx={{ ml: 'auto', height: 20, fontSize: '0.65rem' }} />
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* AI Model */}
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>AI Model</InputLabel>
              <Select
                value={aiModel}
                label="AI Model"
                onChange={(e) => setAiModel(e.target.value)}
                disabled={aiProvider === 'regex_only'}
              >
                {currentProviderModels.map((m) => (
                  <MenuItem key={m} value={m}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <span>{m}</span>
                      {m === providers.find(p => p.id === aiProvider)?.model && (
                        <Chip label="default" size="small" color="primary" sx={{ height: 18, fontSize: '0.6rem' }} />
                      )}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Hybrid text engine selector — only shown for hybrid/OCR engines */}
          {isHybridEngine(engine) && (
            <Grid item xs={12}>
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel>Text Engine for non-image pages</InputLabel>
                <Select
                  value={hybridTextEngine}
                  label="Text Engine for non-image pages"
                  onChange={(e) => setHybridTextEngine(e.target.value)}
                >
                  {TEXT_ENGINES.map((te) => (
                    <MenuItem key={te} value={te}>
                      {te}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                Image-heavy pages (charts, scans) → OCR &nbsp;|&nbsp; Text pages → this engine
              </Typography>
            </Grid>
          )}

          {/* Page Selection */}
          <Grid item xs={6}>
            <TextField
              label="Pages to Extract"
              value={pageNumbers}
              onChange={(e) => setPageNumbers(e.target.value)}
              fullWidth
              placeholder="e.g. 2,3,4 (leave empty for all pages)"
              helperText="Comma-separated page numbers (1-based). Leave empty to extract all pages."
            />
          </Grid>
          <Grid item xs={6} sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
            {[
              { label: 'All Pages', value: '' },
              { label: 'Page 2-3 (Summary)', value: '2,3' },
              { label: 'Page 3-4 (Holdings)', value: '3,4' },
              { label: 'Page 5 (Gains)', value: '5' },
            ].map((preset) => (
              <Chip
                key={preset.label}
                label={preset.label}
                variant={pageNumbers === preset.value ? 'filled' : 'outlined'}
                color={pageNumbers === preset.value ? 'primary' : 'default'}
                onClick={() => setPageNumbers(preset.value)}
                size="small"
              />
            ))}
          </Grid>

          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={loading || !file}
              startIcon={loading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
            >
              {loading ? 'Processing...' : 'Upload & Process'}
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
}
