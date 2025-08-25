import { useState, useEffect, useCallback } from 'react'
import { Download, MessageSquare, Star, Calendar, User, X, Copy, Eye } from 'lucide-react'
import { apiService } from '../services/api'
import { FeedbackSummaryResponse, FeedbackItem } from '../types'

interface AdminFeedbackPanelProps {
  accessLevel: 'visionary_expert' | 'admin';
}

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
}

interface FeedbackModalProps {
  item: FeedbackItem | null;
  isOpen: boolean;
  onClose: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, icon, subtitle }) => (
  <div className="bg-white p-4 sm:p-6 rounded-lg border border-gray-200 hover:shadow-md transition-shadow duration-200">
    <div className="flex items-center justify-between">
      <div className="flex-1 min-w-0">
        <p className="text-xs sm:text-sm text-gray-600 font-medium truncate">{title}</p>
        <p className="text-xl sm:text-2xl font-light text-gray-900 mt-1">{value}</p>
        {subtitle && (
          <p className="text-xs text-gray-500 mt-1 truncate">{subtitle}</p>
        )}
      </div>
      <div className="text-gray-400 ml-2 sm:ml-4 flex-shrink-0">{icon}</div>
    </div>
  </div>
);

const FeedbackModal: React.FC<FeedbackModalProps> = ({ item, isOpen, onClose }) => {
  if (!isOpen || !item) return null;

  const handleCopyFeedback = async () => {
    if (item.comment) {
      await navigator.clipboard.writeText(item.comment);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pl-PL', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderStars = (rating?: number) => {
    if (!rating) return <span className="text-gray-400 text-sm">No rating</span>;
    
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating ? 'text-yellow-500 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-2 text-sm font-medium text-gray-700">{rating}/5</span>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-brand-200/50 max-w-2xl w-full max-h-[80vh] sm:max-h-[85vh] overflow-hidden flex flex-col mx-2 sm:mx-4">
        {/* Header */}
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-brand-200/30 flex items-center justify-between">
          <div>
            <h3 className="text-base sm:text-lg font-medium text-gray-900">Feedback Details</h3>
            <p className="text-sm text-gray-500 mt-1">{formatDate(item.created_at)}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-brand-100 rounded-xl transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-4 sm:space-y-6">
          {/* Rating and User Type */}
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Rating</h4>
              {renderStars(item.rating)}
            </div>
            <div className="text-right">
              <h4 className="text-sm font-medium text-gray-700 mb-2">User Type</h4>
              <span className="px-3 py-1 bg-brand-50 text-brand-700 rounded-full text-sm font-medium">
                {item.user_type}
              </span>
            </div>
          </div>

          {/* Comment */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-700">Comment</h4>
              <button
                onClick={handleCopyFeedback}
                className="flex items-center space-x-1 text-sm text-brand-600 hover:text-brand-700"
              >
                <Copy className="w-4 h-4" />
                <span>Copy</span>
              </button>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-900 whitespace-pre-wrap">
                {item.comment}
              </p>
            </div>
          </div>

          {/* Message ID */}
          {item.message_id && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Message ID</h4>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm text-gray-600 font-mono">{item.message_id}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const AdminFeedbackPanel: React.FC<AdminFeedbackPanelProps> = ({ accessLevel }) => {
  const [feedbackData, setFeedbackData] = useState<FeedbackSummaryResponse | null>(null);
  const [allFeedbacks, setAllFeedbacks] = useState<FeedbackItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [selectedItem, setSelectedItem] = useState<FeedbackItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadFeedbackSummary = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiService.getFeedbackSummary();
      setFeedbackData(response);
      setAllFeedbacks(response.summary.recent_feedback || []);
      
      if (import.meta.env.VITE_TEST_ENV === 'true') {
        console.log('✅ [AdminFeedback] Data loaded:', response);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load feedback data';
      setError(errorMessage);
      console.error('❌ [AdminFeedback] Error loading data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleExportCSV = async () => {
    try {
      setIsExporting(true);
      const blob = await apiService.exportFeedbackCSV();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `feedback_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      if (import.meta.env.VITE_TEST_ENV === 'true') {
        console.log('✅ [AdminFeedback] CSV exported successfully');
      }
    } catch (err) {
      console.error('❌ [AdminFeedback] Export failed:', err);
      setError('Failed to export CSV');
    } finally {
      setIsExporting(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pl-PL', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderStars = (rating?: number) => {
    if (!rating) return <span className="text-gray-400 text-xs">No rating</span>;
    
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-3 h-3 ${
              star <= rating ? 'text-yellow-500 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-1 text-xs font-medium text-gray-600">{rating}</span>
      </div>
    );
  };

  const handleViewDetails = (item: FeedbackItem) => {
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const calculatePositiveRate = () => {
    if (!feedbackData?.summary.rating_distribution) return 0;
    const positive = (feedbackData.summary.rating_distribution[4] || 0) + 
                    (feedbackData.summary.rating_distribution[5] || 0);
    const total = feedbackData.summary.total_feedback;
    return total > 0 ? Math.round((positive / total) * 100) : 0;
  };

  useEffect(() => {
    loadFeedbackSummary();
    const interval = setInterval(loadFeedbackSummary, 60000);
    return () => clearInterval(interval);
  }, [loadFeedbackSummary]);

  if (accessLevel !== 'admin') {
    return (
      <div className="h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-sm border border-gray-200">
          <User className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">Admin access required</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading feedback...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-sm border border-gray-200">
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={loadFeedbackSummary}
            className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-50 flex flex-col overflow-hidden">
      {/* Header - fixed */}
      <div className="bg-gray-50 flex-shrink-0 relative z-10">
        <div className="max-w-7xl mx-auto pl-16 pr-4 sm:px-6 lg:px-8 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 sm:space-x-4">
              <h1 className="text-lg sm:text-xl font-light text-gray-900">Feedback</h1>
              <span className="text-xs sm:text-sm text-gray-500 hidden sm:inline">
                {accessLevel === 'admin' ? 'Admin' : 'Expert'}
              </span>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-4">
              <button
                onClick={handleExportCSV}
                disabled={isExporting}
                className="flex items-center space-x-1 sm:space-x-2 px-3 sm:px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 text-sm"
              >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline text-sm font-medium">Export</span>
              </button>
              <img 
                src="/aquaforest_logo.png" 
                alt="Aquaforest" 
                className="h-5 sm:h-6 opacity-60"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - scrollable */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
          {/* Metrics Grid */}
          {feedbackData && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
              <MetricCard
                title="Total Feedback"
                value={feedbackData.summary.total_feedback || 0}
                icon={<MessageSquare className="w-5 h-5 sm:w-6 sm:h-6" />}
                subtitle="All time"
              />
              <MetricCard
                title="Average Rating"
                value={feedbackData.summary.average_rating?.toFixed(1) || '0.0'}
                icon={<Star className="w-5 h-5 sm:w-6 sm:h-6" />}
                subtitle="Out of 5 stars"
              />
              <MetricCard
                title="Positive Rate"
                value={`${calculatePositiveRate()}%`}
                icon={<User className="w-5 h-5 sm:w-6 sm:h-6" />}
                subtitle="4-5 star ratings"
              />
              <MetricCard
                title="Recent"
                value={allFeedbacks.length}
                icon={<Calendar className="w-5 h-5 sm:w-6 sm:h-6" />}
                subtitle="Last 10 items"
              />
            </div>
          )}

          {/* Recent Feedback - Desktop Table */}
          <div className="bg-white rounded-lg border border-gray-200 hidden sm:block">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-light text-gray-900">Recent Feedback</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rating
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Comment
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {allFeedbacks.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatDate(item.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {renderStars(item.rating)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <p className="truncate max-w-xs" title={item.comment}>
                          {item.comment}
                        </p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                          {item.user_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => handleViewDetails(item)}
                          className="flex items-center space-x-1 text-sm text-brand-600 hover:text-brand-700"
                        >
                          <Eye className="w-4 h-4" />
                          <span>View</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent Feedback - Mobile Cards */}
          <div className="sm:hidden space-y-4">
            <h2 className="text-base font-light text-gray-900 mb-3">Recent Feedback</h2>
            {allFeedbacks.map((item) => (
              <div key={item.id} className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-500">{formatDate(item.created_at)}</p>
                    <p className="text-sm text-gray-900 mt-1 line-clamp-2">{item.comment}</p>
                  </div>
                  <button
                    onClick={() => handleViewDetails(item)}
                    className="ml-2 p-1 text-brand-600"
                  >
                    <Eye className="w-5 h-5" />
                  </button>
                </div>
                <div className="flex items-center justify-between mt-3">
                  {renderStars(item.rating)}
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                    {item.user_type}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Feedback Modal */}
      <FeedbackModal 
        item={selectedItem} 
        isOpen={isModalOpen} 
        onClose={() => {
          setIsModalOpen(false);
          setSelectedItem(null);
        }} 
      />
    </div>
  );
};

export default AdminFeedbackPanel