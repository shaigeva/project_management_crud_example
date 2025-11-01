import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient, { Project } from '../services/api';
import { Navigation } from '../components/Navigation';

export function ProjectDetailsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProject = async () => {
      if (!projectId) {
        setError('No project ID provided');
        setIsLoading(false);
        return;
      }

      try {
        const data = await apiClient.getProject(projectId);
        setProject(data);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Failed to load project');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchProject();
  }, [projectId]);

  if (isLoading) {
    return (
      <>
        <Navigation />
        <div className="project-details-page">
          <div className="loading">Loading project...</div>
        </div>
      </>
    );
  }

  if (error || !project) {
    return (
      <>
        <Navigation />
        <div className="project-details-page">
          <div className="error-message">{error || 'Project not found'}</div>
          <Link to="/projects" className="back-link">
            ← Back to Projects
          </Link>
        </div>
      </>
    );
  }

  return (
    <>
      <Navigation />
      <div className="project-details-page">
        <div className="page-header">
          <div className="header-with-back">
            <Link to="/projects" className="back-link">
              ← Back to Projects
            </Link>
            <h1>{project.name}</h1>
          </div>
        </div>

        <div className="project-details-content">
          <div className="details-section">
            <h2>Project Information</h2>
            <dl className="details-list">
              <dt>Description</dt>
              <dd>{project.description || 'No description provided'}</dd>

              <dt>Status</dt>
              <dd>
                <span className={`status-badge status-${project.status}`}>
                  {project.status}
                </span>
              </dd>

              <dt>Organization ID</dt>
              <dd>{project.organization_id}</dd>

              <dt>Created</dt>
              <dd>{new Date(project.created_at).toLocaleString()}</dd>

              <dt>Last Updated</dt>
              <dd>{new Date(project.updated_at).toLocaleString()}</dd>

              <dt>Archived</dt>
              <dd>{project.is_archived ? 'Yes' : 'No'}</dd>
            </dl>
          </div>

          <div className="details-section">
            <h2>Epics</h2>
            <p className="placeholder-text">Epic management coming soon...</p>
          </div>

          <div className="details-section">
            <h2>Tickets</h2>
            <p className="placeholder-text">Ticket management coming soon...</p>
          </div>
        </div>
      </div>
    </>
  );
}
