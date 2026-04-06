// --- Enums ---

export enum DocumentType {
  STATEMENT = 'statement',
  LETTER = 'letter',
  CONFIRM = 'confirm',
}

export enum StatementType {
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  ANNUAL = 'annual',
  DAILY = 'daily',
}

export enum LetterType {
  WELCOME = 'welcome',
  FEE_CHANGE = 'fee_change',
  ACCOUNT_UPDATE = 'account_update',
  CLOSURE = 'closure',
  REGULATORY = 'regulatory',
}

export enum ConfirmType {
  TRADE = 'trade',
  TRANSFER = 'transfer',
  DIVIDEND = 'dividend',
  INTEREST = 'interest',
  CORPORATE_ACTION = 'corporate_action',
}

export enum ProductType {
  EQUITIES = 'equities',
  FIXED_INCOME = 'fixed_income',
  MUTUAL_FUNDS = 'mutual_funds',
  OPTIONS = 'options',
  FUTURES = 'futures',
  ALL = 'all',
}

export enum ExtractionEngine {
  PYMUPDF = 'pymupdf',
  PDFPLUMBER = 'pdfplumber',
  TIKA = 'tika',
  PDFMINER = 'pdfminer',
  PEGBOX = 'pegbox',
  PDFBOX = 'pdfbox',
  OCR_PYTESSERACT = 'ocr_pytesseract',
  OCR_AZURE = 'ocr_azure',
  HYBRID_OCR_PYTESSERACT = 'hybrid_pytesseract',
  HYBRID_OCR_AZURE = 'hybrid_azure',
}

export enum ComparisonStatus {
  MATCH = 'match',
  MISMATCH = 'mismatch',
  MISSING_IN_PDF = 'missing_in_pdf',
  MISSING_IN_DB = 'missing_in_db',
  NOT_COMPARED = 'not_compared',
}

// --- AI Provider ---

export enum AIProvider {
  OPENAI = 'openai',
  GITHUB_COPILOT = 'github_copilot',
  ANTHROPIC = 'anthropic',
  GOOGLE_GEMINI = 'google_gemini',
  DEEPSEEK = 'deepseek',
  REGEX_ONLY = 'regex_only',
}

export interface AIProviderStatus {
  id: string;
  name: string;
  configured: boolean;
  model: string;
  available_models: string[];
}

export interface AIProvidersResponse {
  current_provider: string;
  providers: AIProviderStatus[];
}

// --- Request Types ---

export interface AccountNumber {
  office: string;
  account: string;
}

export interface StatementInput {
  start_date: string;
  end_date: string;
  statement_type: StatementType;
  product_type: ProductType;
}

export interface LetterInput {
  letter_type: LetterType;
  load_date: string;
}

export interface ConfirmInput {
  start_date: string;
  end_date: string;
  confirm_type: ConfirmType;
  product_type: ProductType;
}

export interface ProcessSingleRequest {
  account_number: AccountNumber;
  document_type: DocumentType;
  extraction_engine: ExtractionEngine;
  statement_input?: StatementInput;
  letter_input?: LetterInput;
  confirm_input?: ConfirmInput;
}

export interface ProcessBatchRequest {
  requests: ProcessSingleRequest[];
}

// --- Response Types ---

export interface FieldComparison {
  field_name: string;
  pdf_value: string | null;
  db_value: string | null;
  status: ComparisonStatus;
  confidence: number;
}

// --- Pipeline Debug Types ---

export interface StepTiming {
  step_name: string;
  duration_ms: number;
  status: string;
}

export interface PageDetail {
  page_number: number;
  method: string;
  engine: string;
  is_image_dominant: boolean;
  image_count: number;
  image_coverage_pct: number;
  text_chars: number;
  text_density: number;
  confidence: number;
  extracted_text: string;
  detection_reason: string;
}

export interface AIModelInfo {
  model_name: string;
  provider: string;
  provider_display: string;
  temperature: number;
  max_tokens: number;
  total_prompt_chars: number;
  text_chunk_sent_chars: number;
  text_chunk_max_chars: number;
  prompt_template_chars: number;
  method_used: string;
  ai_request_prompt: string;
  ai_response_raw: string;
  response_parse_success: boolean;
  error_message: string | null;
}

export interface DataCategory {
  category_name: string;
  fields: Record<string, unknown>;
}

export interface DebugInfo {
  // Timing
  total_processing_ms: number;
  step_timings: StepTiming[];

  // Extraction
  extraction_engine_used: string | null;
  extraction_text_engine: string | null;
  extraction_page_count: number;
  extraction_text_length: number;
  ocr_fallback_used: boolean;
  parallel_execution: boolean;

  // Page-level
  page_details: PageDetail[];
  ocr_pages_count: number;
  text_pages_count: number;

  // Raw text
  extracted_text: string;

  // AI model
  ai_model_info: AIModelInfo | null;

  // Data segregation
  data_categories: DataCategory[];

  // Classified output
  classified_output: Record<string, unknown>;

  // Legacy
  ai_prompt: string;
}

export interface ComparisonResult {
  account_number: string;
  document_type: DocumentType;
  extraction_engine: ExtractionEngine;
  field_comparisons: FieldComparison[];
  overall_match: boolean;
  match_count: number;
  mismatch_count: number;
  missing_count: number;
  confidence_score: number;
  processing_time_ms: number;
  timestamp: string;
  error?: string;
  debug_info?: DebugInfo;
}

export interface HealthResponse {
  status: string;
  version: string;
  services: {
    snowflake: string;
    db2: string;
    springboot: string;
  };
  timestamp: string;
}
