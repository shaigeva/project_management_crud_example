import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../services/api';

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

export function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const { logout } = useAuth();

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await apiClient.getProjects();
        setProjects(data);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Failed to load projects');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchProjects();
  }, []);

  return (
    <div className="projects-page">
      <header className="page-header">
        <h1>Projects</h1>
        <button onClick={logout} className="logout-button">
          Logout
        </button>
      </header>

      {isLoading && <div className="loading">Loading projects...</div>}

      {error && <div className="error-message">{error}</div>}

      {!isLoading && !error && (
        <div className="projects-list">
          {projects.length === 0 ? (
            <p>No projects found</p>
          ) : (
            <table className="projects-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((project) => (
                  <tr key={project.id}>
                    <td>{project.name}</td>
                    <td>{project.description}</td>
                    <td>
                      <span className={`status-badge status-${project.status}`}>
                        {project.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
