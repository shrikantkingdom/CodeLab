import apiClient from './client';
import type {
  ProcessSingleRequest,
  ProcessBatchRequest,
  ComparisonResult,
  HealthResponse,
  AIProvidersResponse,
} from '../types';

export const processSingle = async (request: ProcessSingleRequest): Promise<ComparisonResult> => {
  const { data } = await apiClient.post<ComparisonResult>('/process-single', request);
  return data;
};

export const uploadAndProcess = async (formData: FormData): Promise<ComparisonResult> => {
  const { data } = await apiClient.post<ComparisonResult>('/upload-and-process', formData, {
    headers: { 'Content-Type': undefined },
  });
  return data;
};

export const processBatch = async (request: ProcessBatchRequest): Promise<ComparisonResult[]> => {
  const { data } = await apiClient.post<ComparisonResult[]>('/process-batch', request);
  return data;
};

export const getCompareResults = async (
  accountNumber?: string,
  limit = 50
): Promise<ComparisonResult[]> => {
  const params: Record<string, string | number> = { limit };
  if (accountNumber) params.account_number = accountNumber;
  const { data } = await apiClient.get<ComparisonResult[]>('/compare-results', { params });
  return data;
};

export const getHealth = async (): Promise<HealthResponse> => {
  const { data } = await apiClient.get<HealthResponse>('/health');
  return data;
};

export const getAIProviders = async (): Promise<AIProvidersResponse> => {
  const { data } = await apiClient.get<AIProvidersResponse>('/ai-providers');
  return data;
};
