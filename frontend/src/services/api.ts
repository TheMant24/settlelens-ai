// API service for backend communication

import type { InvestigateRequest, InvestigateResponse, ErrorResponse } from '../types/investigation';

// API URL from environment variables (Vite)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
    this.name = 'ApiError';
  }
}

export async function investigateTransaction(
  transactionId: string
): Promise<InvestigateResponse> {
  const request: InvestigateRequest = { transaction_id: transactionId };

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/investigate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
  } catch (err) {
    // Network error - backend is down or unreachable
    const message = err instanceof Error ? err.message : 'Network error';
    throw new ApiError(
      0,
      `Unable to reach the investigation service at ${API_BASE_URL}. ` +
        `Please ensure the backend is running. (${message})`
    );
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const errorBody = (await response.json()) as ErrorResponse;
      if (errorBody.detail) {
        detail = errorBody.detail;
      }
    } catch {
      // Could not parse error body
    }
    throw new ApiError(response.status, detail);
  }

  return (await response.json()) as InvestigateResponse;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}