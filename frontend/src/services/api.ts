import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = 'http://localhost:8000';

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
