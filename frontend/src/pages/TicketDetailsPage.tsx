import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient, { Ticket, User } from '../services/api';
import { Navigation } from '../components/Navigation';

export function TicketDetailsPage() {
  const { ticketId } = useParams<{ ticketId: string }>();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [users, setUsers] = useState<User[]>([]);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [isUpdatingAssignee, setIsUpdatingAssignee] = useState(false);

  useEffect(() => {
    const fetchTicket = async () => {
      if (!ticketId) {
        setError('No ticket ID provided');
        setIsLoading(false);
        return;
      }

      try {
        const [ticketData, usersData] = await Promise.all([
          apiClient.getTicket(ticketId),
          apiClient.getUsers(),
        ]);
        setTicket(ticketData);
        setUsers(usersData);
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

  const handleStatusChange = async (newStatus: string) => {
    if (!ticketId) return;

    setIsUpdatingStatus(true);
    try {
      const updatedTicket = await apiClient.updateTicketStatus(ticketId, newStatus);
      setTicket(updatedTicket);
    } catch (err) {
      console.error('Failed to update status:', err);
      alert('Failed to update ticket status');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleAssigneeChange = async (assigneeId: string) => {
    if (!ticketId) return;

    setIsUpdatingAssignee(true);
    try {
      const updatedTicket = await apiClient.updateTicketAssignee(
        ticketId,
        assigneeId || null
      );
      setTicket(updatedTicket);
    } catch (err) {
      console.error('Failed to update assignee:', err);
      alert('Failed to update ticket assignee');
    } finally {
      setIsUpdatingAssignee(false);
    }
  };

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
                <select
                  value={ticket.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  disabled={isUpdatingStatus}
                  className="status-select"
                >
                  <option value="TODO">TODO</option>
                  <option value="IN_PROGRESS">IN_PROGRESS</option>
                  <option value="DONE">DONE</option>
                </select>
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

              <dt>Reporter</dt>
              <dd>{users.find(u => u.id === ticket.reporter_id)?.full_name || ticket.reporter_id}</dd>

              <dt>Assignee</dt>
              <dd>
                <select
                  value={ticket.assignee_id || ''}
                  onChange={(e) => handleAssigneeChange(e.target.value)}
                  disabled={isUpdatingAssignee}
                  className="assignee-select"
                >
                  <option value="">Unassigned</option>
                  {users.filter(u => u.is_active).map(user => (
                    <option key={user.id} value={user.id}>
                      {user.full_name} ({user.username})
                    </option>
                  ))}
                </select>
              </dd>

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
