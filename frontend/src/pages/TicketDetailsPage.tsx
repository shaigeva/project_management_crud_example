import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient, { Ticket } from '../services/api';
import { Navigation } from '../components/Navigation';

export function TicketDetailsPage() {
  const { ticketId } = useParams<{ ticketId: string }>();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTicket = async () => {
      if (!ticketId) {
        setError('No ticket ID provided');
        setIsLoading(false);
        return;
      }

      try {
        const data = await apiClient.getTicket(ticketId);
        setTicket(data);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Failed to load ticket');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchTicket();
  }, [ticketId]);

  if (isLoading) {
    return (
      <>
        <Navigation />
        <div className="ticket-details-page">
          <div className="loading">Loading ticket...</div>
        </div>
      </>
    );
  }

  if (error || !ticket) {
    return (
      <>
        <Navigation />
        <div className="ticket-details-page">
          <div className="error-message">{error || 'Ticket not found'}</div>
          <Link to={`/projects/${ticket?.project_id || ''}`} className="back-link">
            ← Back to Project
          </Link>
        </div>
      </>
    );
  }

  return (
    <>
      <Navigation />
      <div className="ticket-details-page">
        <div className="page-header">
          <div className="header-with-back">
            <Link to={`/projects/${ticket.project_id}`} className="back-link">
              ← Back to Project
            </Link>
            <h1>{ticket.title}</h1>
          </div>
        </div>

        <div className="ticket-details-content">
          <div className="details-section">
            <h2>Ticket Information</h2>
            <dl className="details-list">
              <dt>Description</dt>
              <dd>{ticket.description || 'No description provided'}</dd>

              <dt>Status</dt>
              <dd>
                <span className={`status-badge status-${ticket.status.toLowerCase()}`}>
                  {ticket.status}
                </span>
              </dd>

              <dt>Priority</dt>
              <dd>
                {ticket.priority ? (
                  <span className={`priority-badge priority-${ticket.priority.toLowerCase()}`}>
                    {ticket.priority}
                  </span>
                ) : (
                  'Not set'
                )}
              </dd>

              <dt>Reporter ID</dt>
              <dd>{ticket.reporter_id}</dd>

              <dt>Assignee ID</dt>
              <dd>{ticket.assignee_id || 'Unassigned'}</dd>

              <dt>Project ID</dt>
              <dd>{ticket.project_id}</dd>

              <dt>Created</dt>
              <dd>{new Date(ticket.created_at).toLocaleString()}</dd>

              <dt>Last Updated</dt>
              <dd>{new Date(ticket.updated_at).toLocaleString()}</dd>
            </dl>
          </div>
        </div>
      </div>
    </>
  );
}
