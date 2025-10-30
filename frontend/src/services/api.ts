import axios, { AxiosInstance } from 'axios';

// Use E2E port during E2E testing, dev port otherwise
const API_BASE_URL = import.meta.env.VITE_E2E_TESTING === 'true'
  ? 'http://localhost:18000'
  : 'http://localhost:8000';

interface HealthResponse {
  status: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async getHealth(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
