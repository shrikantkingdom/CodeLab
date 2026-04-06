import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Box, Typography, ToggleButtonGroup, ToggleButton, Snackbar, Alert } from '@mui/material';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import SingleInputForm from '../components/SingleInputForm';
import FileUploadForm from '../components/FileUploadForm';
import ComparisonTable from '../components/ComparisonTable';
import PipelineDebugPanel from '../components/PipelineDebugPanel';
import { processSingle, uploadAndProcess } from '../api/deraiApi';
import type { ProcessSingleRequest, ComparisonResult } from '../types';

type ProcessMode = 'url' | 'upload';

interface ToastState {
  open: boolean;
  severity: 'success' | 'error' | 'warning' | 'info';
  message: string;
}

export default function ProcessPage() {
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [mode, setMode] = useState<ProcessMode>('upload');
  const [toast, setToast] = useState<ToastState>({ open: false, severity: 'success', message: '' });

  const showToast = (severity: ToastState['severity'], message: string) =>
    setToast({ open: true, severity, message });

  const urlMutation = useMutation({
    mutationFn: (request: ProcessSingleRequest) => processSingle(request),
    onSuccess: (data) => {
      setResult(data);
      const aiInfo = data.debug_info?.ai_model_info;
      if (aiInfo?.error_message) {
        showToast('warning', aiInfo.error_message);
      } else if (aiInfo?.method_used?.includes('_api')) {
        showToast('success', `AI classification succeeded via ${aiInfo.provider_display || aiInfo.method_used}`);
      } else if (aiInfo?.method_used === 'regex_fallback' || aiInfo?.method_used === 'regex_only') {
        showToast('info', `Used ${aiInfo.method_used === 'regex_only' ? 'regex-only mode' : 'regex fallback'} — no AI call made`);
      }
    },
    onError: (err) => showToast('error', (err as Error).message || 'Processing failed'),
  });

  const uploadMutation = useMutation({
    mutationFn: (formData: FormData) => uploadAndProcess(formData),
    onSuccess: (data) => {
      setResult(data);
      const aiInfo = data.debug_info?.ai_model_info;
      if (aiInfo?.error_message) {
        showToast('warning', aiInfo.error_message);
      } else if (aiInfo?.method_used?.includes('_api')) {
        showToast('success', `AI classification succeeded via ${aiInfo.provider_display || aiInfo.method_used}`);
      } else if (aiInfo?.method_used === 'regex_fallback' || aiInfo?.method_used === 'regex_only') {
        showToast('info', `Used ${aiInfo.method_used === 'regex_only' ? 'regex-only mode' : 'regex fallback'} — no AI call made`);
      }
    },
    onError: (err) => showToast('error', (err as Error).message || 'Processing failed'),
  });

  const handleUrlSubmit = (request: ProcessSingleRequest) => {
    setResult(null);
    urlMutation.mutate(request);
  };

  const handleUploadSubmit = (formData: FormData) => {
    setResult(null);
    uploadMutation.mutate(formData);
  };

  const isLoading = urlMutation.isPending || uploadMutation.isPending;
  const error = urlMutation.error || uploadMutation.error;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Process Document
      </Typography>

      <ToggleButtonGroup
        value={mode}
        exclusive
        onChange={(_, v) => v && setMode(v)}
        sx={{ mb: 3 }}
      >
        <ToggleButton value="upload">
          <UploadFileIcon sx={{ mr: 1 }} /> Upload from Local
        </ToggleButton>
        <ToggleButton value="url">
          <CloudDownloadIcon sx={{ mr: 1 }} /> Download from URL
        </ToggleButton>
      </ToggleButtonGroup>

      {mode === 'url' ? (
        <SingleInputForm
          onSubmit={handleUrlSubmit}
          loading={isLoading}
          error={error ? (error as Error).message : null}
        />
      ) : (
        <FileUploadForm
          onSubmit={handleUploadSubmit}
          loading={isLoading}
          error={error ? (error as Error).message : null}
        />
      )}

      {result && <ComparisonTable result={result} />}
      {result?.debug_info && <PipelineDebugPanel debugInfo={result.debug_info} />}

      {/* Toast notifications */}
      <Snackbar
        open={toast.open}
        autoHideDuration={8000}
        onClose={() => setToast((t) => ({ ...t, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setToast((t) => ({ ...t, open: false }))}
          severity={toast.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
