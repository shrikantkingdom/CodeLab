import { useState } from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Box,
  Paper,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import TimerIcon from '@mui/icons-material/Timer';
import DescriptionIcon from '@mui/icons-material/Description';
import DataObjectIcon from '@mui/icons-material/DataObject';
import CategoryIcon from '@mui/icons-material/Category';
import ImageIcon from '@mui/icons-material/Image';
import SendIcon from '@mui/icons-material/Send';
import ReceiveIcon from '@mui/icons-material/CallReceived';
import type { DebugInfo, StepTiming, PageDetail, DataCategory } from '../types';

interface Props {
  debugInfo: DebugInfo;
}

/* ── Compact cell style applied to all tables ── */
const denseCellSx = { px: 1, py: 0.5, fontSize: '0.78rem', lineHeight: 1.3 } as const;
const denseHeadSx = { ...denseCellSx, fontWeight: 700 } as const;

/* ── Reusable pre-block style ── */
const preBoxSx = {
  maxHeight: 400,
  overflow: 'auto',
  bgcolor: 'grey.50',
  p: 1.5,
  borderRadius: 1,
  fontSize: '0.78rem',
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-word',
  border: '1px solid',
  borderColor: 'grey.200',
  fontFamily: '"JetBrains Mono", "Fira Code", monospace',
} as const;

/* helper: colour for detection reason */
function reasonColor(reason: string): 'error' | 'warning' | 'info' | 'default' {
  if (reason === 'low_text_with_images' || reason === 'high_image_coverage') return 'error';
  if (reason === 'low_text_density') return 'warning';
  if (reason === 'force_all') return 'info';
  return 'default';
}

/* helper: info chip */
function InfoChip({ label, value }: { label: string; value: string }) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <Typography variant="caption" color="text.secondary">{label}:</Typography>
      <Chip label={value} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.72rem' }} />
    </Box>
  );
}

/* ── Sub-components ── */

function StepTimingsTable({ steps, totalMs }: { steps: StepTiming[]; totalMs: number }) {
  return (
    <TableContainer>
      <Table size="small" sx={{ tableLayout: 'auto' }}>
        <TableHead>
          <TableRow>
            <TableCell sx={denseHeadSx}>#</TableCell>
            <TableCell sx={denseHeadSx}>Step</TableCell>
            <TableCell sx={denseHeadSx} align="right">ms</TableCell>
            <TableCell sx={denseHeadSx} align="right">%</TableCell>
            <TableCell sx={{ ...denseHeadSx, width: 120 }}></TableCell>
            <TableCell sx={denseHeadSx}>Status</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {steps.map((s, i) => {
            const pct = totalMs > 0 ? (s.duration_ms / totalMs) * 100 : 0;
            return (
              <TableRow key={i}>
                <TableCell sx={denseCellSx}>{i + 1}</TableCell>
                <TableCell sx={denseCellSx}>{s.step_name}</TableCell>
                <TableCell sx={denseCellSx} align="right">{s.duration_ms.toFixed(0)}</TableCell>
                <TableCell sx={denseCellSx} align="right">{pct.toFixed(0)}%</TableCell>
                <TableCell sx={denseCellSx}>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(pct, 100)}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </TableCell>
                <TableCell sx={denseCellSx}>
                  <Chip
                    label={s.status}
                    size="small"
                    color={s.status === 'completed' ? 'success' : s.status === 'failed' ? 'error' : 'default'}
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
                </TableCell>
              </TableRow>
            );
          })}
          <TableRow sx={{ bgcolor: 'grey.50' }}>
            <TableCell sx={denseCellSx} />
            <TableCell sx={{ ...denseCellSx, fontWeight: 700 }}>Total</TableCell>
            <TableCell sx={{ ...denseCellSx, fontWeight: 700 }} align="right">{totalMs.toFixed(0)}</TableCell>
            <TableCell sx={{ ...denseCellSx, fontWeight: 700 }} align="right">100%</TableCell>
            <TableCell sx={denseCellSx} />
            <TableCell sx={denseCellSx} />
          </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
  );
}

function PageDetailsTable({ pages }: { pages: PageDetail[] }) {
  return (
    <TableContainer>
      <Table size="small" sx={{ tableLayout: 'auto' }}>
        <TableHead>
          <TableRow>
            <TableCell sx={denseHeadSx}>Pg</TableCell>
            <TableCell sx={denseHeadSx}>Method / Engine</TableCell>
            <TableCell sx={denseHeadSx} align="center">Img?</TableCell>
            <TableCell sx={denseHeadSx} align="right">Imgs</TableCell>
            <TableCell sx={denseHeadSx} align="right">Cov%</TableCell>
            <TableCell sx={denseHeadSx} align="right">Chars</TableCell>
            <TableCell sx={denseHeadSx} align="right">Conf</TableCell>
            <TableCell sx={denseHeadSx}>Reason</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {pages.map((p) => (
            <TableRow key={p.page_number} sx={p.is_image_dominant ? { bgcolor: 'error.50' } : undefined}>
              <TableCell sx={denseCellSx}>{p.page_number}</TableCell>
              <TableCell sx={denseCellSx}>
                <Chip
                  label={`${p.method.toUpperCase()} · ${p.engine}`}
                  size="small"
                  color={p.method === 'ocr' ? 'error' : 'success'}
                  sx={{ height: 20, fontSize: '0.7rem' }}
                />
              </TableCell>
              <TableCell sx={denseCellSx} align="center">
                {p.is_image_dominant ? (
                  <Tooltip title="Image-dominant page">
                    <Chip label="Y" size="small" color="error" sx={{ height: 18, fontSize: '0.65rem', minWidth: 24 }} />
                  </Tooltip>
                ) : (
                  <Chip label="N" size="small" variant="outlined" sx={{ height: 18, fontSize: '0.65rem', minWidth: 24 }} />
                )}
              </TableCell>
              <TableCell sx={denseCellSx} align="right">{p.image_count}</TableCell>
              <TableCell sx={denseCellSx} align="right">{p.image_coverage_pct.toFixed(0)}%</TableCell>
              <TableCell sx={denseCellSx} align="right">{p.text_chars}</TableCell>
              <TableCell sx={denseCellSx} align="right">{(p.confidence * 100).toFixed(0)}%</TableCell>
              <TableCell sx={denseCellSx}>
                <Chip
                  label={p.detection_reason || '—'}
                  size="small"
                  color={reasonColor(p.detection_reason)}
                  variant="outlined"
                  sx={{ height: 20, fontSize: '0.65rem' }}
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

function DataCategoriesView({ categories }: { categories: DataCategory[] }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      {categories.map((cat, i) => (
        <Paper key={i} variant="outlined" sx={{ p: 1 }}>
          <Typography variant="subtitle2" color="primary" sx={{ mb: 0.5, fontSize: '0.8rem' }}>
            {cat.category_name}
          </Typography>
          <Table size="small">
            <TableBody>
              {Object.entries(cat.fields).map(([key, val]) => (
                <TableRow key={key}>
                  <TableCell sx={{ ...denseCellSx, fontFamily: 'monospace', color: 'text.secondary', width: '40%' }}>{key}</TableCell>
                  <TableCell sx={{ ...denseCellSx, fontFamily: 'monospace' }}>
                    {val == null ? (
                      <Typography color="text.disabled" component="span" fontSize="0.78rem">null</Typography>
                    ) : typeof val === 'object' ? (
                      <Box component="pre" sx={{ m: 0, fontSize: '0.75rem', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                        {JSON.stringify(val, null, 2)}
                      </Box>
                    ) : (
                      String(val)
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      ))}
    </Box>
  );
}

function ClassifiedFieldsTable({ data }: { data: Record<string, unknown> }) {
  const entries = Object.entries(data);
  if (entries.length === 0) {
    return <Typography color="text.secondary">No classified output.</Typography>;
  }
  return (
    <TableContainer>
      <Table size="small" sx={{ tableLayout: 'auto' }}>
        <TableHead>
          <TableRow>
            <TableCell sx={{ ...denseHeadSx, width: 30 }}>#</TableCell>
            <TableCell sx={{ ...denseHeadSx, width: '35%' }}>Field</TableCell>
            <TableCell sx={denseHeadSx}>Value</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {entries.map(([key, val], i) => (
            <TableRow key={key}>
              <TableCell sx={denseCellSx}>{i + 1}</TableCell>
              <TableCell sx={{ ...denseCellSx, fontFamily: 'monospace' }}>{key}</TableCell>
              <TableCell sx={{ ...denseCellSx, fontFamily: 'monospace', wordBreak: 'break-word' }}>
                {val == null ? (
                  <Typography color="text.disabled" component="span" fontSize="0.78rem">null</Typography>
                ) : typeof val === 'object' ? (
                  <Box component="pre" sx={{ m: 0, fontSize: '0.75rem', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {JSON.stringify(val, null, 2)}
                  </Box>
                ) : (
                  String(val)
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

/* ── Main component ── */

export default function PipelineDebugPanel({ debugInfo }: Props) {
  const [expanded, setExpanded] = useState<string | false>(false);

  const toggle = (panel: string) => (_: unknown, open: boolean) => {
    setExpanded(open ? panel : false);
  };

  const ai = debugInfo.ai_model_info;
  const steps = debugInfo.step_timings ?? [];
  const pages = debugInfo.page_details ?? [];
  const categories = debugInfo.data_categories ?? [];

  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      {/* ── Header chips ── */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, flexWrap: 'wrap' }}>
        <Typography variant="h6" sx={{ mr: 1 }}>Pipeline Observability</Typography>
        <Chip label={`Total: ${debugInfo.total_processing_ms?.toFixed(0) ?? '?'} ms`} size="small" color="primary" />
        <Chip label={`Engine: ${debugInfo.extraction_engine_used ?? '—'}`} size="small" variant="outlined" />
        {debugInfo.extraction_text_engine && (
          <Chip label={`Text engine: ${debugInfo.extraction_text_engine}`} size="small" variant="outlined" />
        )}
        <Chip label={`${debugInfo.extraction_page_count} pages`} size="small" variant="outlined" />
        <Chip label={`${debugInfo.extraction_text_length} chars`} size="small" variant="outlined" />
        {debugInfo.ocr_fallback_used && <Chip label="OCR Fallback" size="small" color="warning" />}
        <Chip label={debugInfo.parallel_execution ? 'Parallel: ON' : 'Parallel: OFF'} size="small" variant="outlined" />
        {debugInfo.ocr_pages_count > 0 && (
          <Chip label={`OCR pages: ${debugInfo.ocr_pages_count}`} size="small" color="error" variant="outlined" />
        )}
        {debugInfo.text_pages_count > 0 && (
          <Chip label={`Text pages: ${debugInfo.text_pages_count}`} size="small" color="success" variant="outlined" />
        )}
      </Box>
      <Divider sx={{ mb: 1 }} />

      {/* ───── 1. Step Timings ───── */}
      <Accordion expanded={expanded === 'timings'} onChange={toggle('timings')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TimerIcon color="primary" fontSize="small" />
            <Typography fontWeight={600}>Step-by-Step Execution Timing</Typography>
            <Chip label={`${steps.length} steps`} size="small" color="primary" variant="outlined" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <StepTimingsTable steps={steps} totalMs={debugInfo.total_processing_ms} />
        </AccordionDetails>
      </Accordion>

      {/* ───── 2. Page-Level Extraction ───── */}
      <Accordion expanded={expanded === 'pages'} onChange={toggle('pages')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ImageIcon color="secondary" fontSize="small" />
            <Typography fontWeight={600}>Page-Level Extraction Details</Typography>
            <Chip label={`${pages.length} pages analysed`} size="small" color="secondary" variant="outlined" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {pages.length > 0 ? <PageDetailsTable pages={pages} /> : (
            <Typography color="text.secondary">No page-level data (non-hybrid engine).</Typography>
          )}
        </AccordionDetails>
      </Accordion>

      {/* ───── 3. Extracted Text ───── */}
      <Accordion expanded={expanded === 'extracted'} onChange={toggle('extracted')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DescriptionIcon color="primary" fontSize="small" />
            <Typography fontWeight={600}>Extracted Text (Full)</Typography>
            <Chip label={`${debugInfo.extraction_text_length} chars`} size="small" color="primary" variant="outlined" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box component="pre" sx={preBoxSx}>
            {debugInfo.extracted_text || '(No text extracted)'}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* ───── 4. AI Model — Request ───── */}
      <Accordion expanded={expanded === 'ai_request'} onChange={toggle('ai_request')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SendIcon color="info" fontSize="small" />
            <Typography fontWeight={600}>AI Model Request</Typography>
            {ai && <Chip label={`Model: ${ai.model_name || '—'}`} size="small" color="info" variant="outlined" />}
            {ai && <Chip label={`Provider: ${ai.provider_display || ai.provider || '—'}`} size="small" variant="outlined" />}
            {ai && <Chip label={`Method: ${ai.method_used}`} size="small" variant="outlined" />}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {ai ? (
            <Box>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
                <InfoChip label="Model" value={ai.model_name} />
                <InfoChip label="Provider" value={ai.provider_display || ai.provider || '—'} />
                <InfoChip label="Temperature" value={String(ai.temperature)} />
                <InfoChip label="Max Tokens" value={String(ai.max_tokens)} />
                <InfoChip label="Method" value={ai.method_used} />
                <InfoChip label="Prompt template chars" value={String(ai.prompt_template_chars)} />
                <InfoChip label="Text chunk sent" value={`${ai.text_chunk_sent_chars} / ${ai.text_chunk_max_chars} chars`} />
                <InfoChip label="Total prompt chars" value={String(ai.total_prompt_chars)} />
              </Box>
              <Typography variant="subtitle2" sx={{ mb: 0.5 }}>Full Prompt Sent to AI:</Typography>
              <Box component="pre" sx={preBoxSx}>
                {ai.ai_request_prompt || '(no prompt — regex fallback)'}
              </Box>
            </Box>
          ) : (
            <Typography color="text.secondary">No AI model info available.</Typography>
          )}
        </AccordionDetails>
      </Accordion>

      {/* ───── 5. AI Model — Response ───── */}
      <Accordion expanded={expanded === 'ai_response'} onChange={toggle('ai_response')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ReceiveIcon color="secondary" fontSize="small" />
            <Typography fontWeight={600}>AI Model Response</Typography>
            {ai && (
              <Chip
                label={
                  ai.method_used === 'regex_fallback' || ai.method_used === 'regex_only'
                    ? ai.error_message ? 'AI Error → Regex Fallback' : ai.method_used === 'regex_only' ? 'Regex Only' : 'Regex Fallback'
                    : ai.response_parse_success ? 'Parsed OK' : 'Parse Failed'
                }
                size="small"
                color={
                  ai.error_message ? 'error'
                    : (ai.method_used === 'regex_fallback' || ai.method_used === 'regex_only') ? 'warning'
                    : ai.response_parse_success ? 'success' : 'error'
                }
              />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {ai ? (
            ai.method_used === 'regex_fallback' || ai.method_used === 'regex_only' ? (
              <Box sx={{ p: 2, bgcolor: 'warning.50', borderRadius: 1, border: '1px solid', borderColor: 'warning.200' }}>
                {ai.error_message ? (
                  <>
                    <Typography variant="subtitle2" color="error.dark" gutterBottom>
                      AI Error: {ai.error_message}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      The pipeline fell back to <strong>regex pattern matching</strong> because the AI provider
                      ({ai.provider_display || ai.provider || 'unknown'}) returned an error.
                    </Typography>
                  </>
                ) : (
                  <>
                    <Typography variant="subtitle2" color="warning.dark" gutterBottom>
                      {ai.method_used === 'regex_only' ? 'Regex-Only Mode Selected' : 'No API Key Configured'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {ai.method_used === 'regex_only'
                        ? 'You selected "Regex Only" mode — no AI call was made.'
                        : `No API key is configured for ${ai.provider_display || ai.provider || 'the selected provider'}. Set the key in .env and restart.`}
                    </Typography>
                  </>
                )}
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Regex fallback extracts field values via pattern matching on raw text.
                  Results may be less accurate than LLM-based extraction.
                </Typography>
                {ai.ai_response_raw && (
                  <Box component="pre" sx={{ ...preBoxSx, mt: 1 }}>
                    {ai.ai_response_raw}
                  </Box>
                )}
              </Box>
            ) : (
              <Box component="pre" sx={preBoxSx}>
                {ai.ai_response_raw || '(empty response)'}
              </Box>
            )
          ) : (
            <Typography color="text.secondary">No AI response data.</Typography>
          )}
        </AccordionDetails>
      </Accordion>

      {/* ───── 6. Data Categories (pre-classification segregation) ───── */}
      <Accordion expanded={expanded === 'categories'} onChange={toggle('categories')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CategoryIcon color="warning" fontSize="small" />
            <Typography fontWeight={600}>Data Segregation (Categories)</Typography>
            <Chip label={`${categories.length} categories`} size="small" color="warning" variant="outlined" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {categories.length > 0 ? (
            <DataCategoriesView categories={categories} />
          ) : (
            <Typography color="text.secondary">No category segregation available.</Typography>
          )}
        </AccordionDetails>
      </Accordion>

      {/* ───── 7. Classified Output (final fields & values) ───── */}
      <Accordion expanded={expanded === 'classification'} onChange={toggle('classification')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DataObjectIcon color="success" fontSize="small" />
            <Typography fontWeight={600}>Final Classified Output (Fields & Values)</Typography>
            <Chip
              label={`${Object.keys(debugInfo.classified_output ?? {}).length} fields`}
              size="small"
              color="success"
              variant="outlined"
            />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <ClassifiedFieldsTable data={debugInfo.classified_output ?? {}} />
        </AccordionDetails>
      </Accordion>

      {/* ───── 8. Page-Level Extracted Text ───── */}
      {pages.some(p => p.extracted_text) && (
        <Accordion expanded={expanded === 'page_text'} onChange={toggle('page_text')}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <DescriptionIcon color="secondary" fontSize="small" />
              <Typography fontWeight={600}>Per-Page Extracted Text</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            {pages.filter(p => p.extracted_text).map(p => (
              <Box key={p.page_number} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', gap: 1, mb: 0.5, alignItems: 'center' }}>
                  <Typography variant="subtitle2">Page {p.page_number}</Typography>
                  <Chip label={p.method.toUpperCase()} size="small" color={p.method === 'ocr' ? 'error' : 'success'} />
                  <Chip label={p.engine} size="small" variant="outlined" />
                  <Chip label={`${p.extracted_text.length} chars`} size="small" variant="outlined" />
                </Box>
                <Box component="pre" sx={{ ...preBoxSx, maxHeight: 200 }}>
                  {p.extracted_text}
                </Box>
              </Box>
            ))}
          </AccordionDetails>
        </Accordion>
      )}
    </Paper>
  );
}
