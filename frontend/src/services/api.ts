import axios, { AxiosInstance } from 'axios';

// Use E2E port during E2E testing, dev port otherwise
const API_BASE_URL = import.meta.env.VITE_E2E_TESTING === 'true'
  ? 'http://localhost:18000'
  : 'http://localhost:8000';

interface HealthResponse {
  status: string;
}

interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  organization_id: string | null;
  role: string;
}

interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
  organization_id: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });
  }

  setToken(token: string | null) {
    this.token = token;
  }

  async getHealth(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>('/auth/login', credentials);
    return response.data;
  }

  async getProjects(): Promise<Project[]> {
    const response = await this.client.get<Project[]>('/api/projects');
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
