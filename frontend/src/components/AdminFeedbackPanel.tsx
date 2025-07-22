import { useState, useEffect, useRef, useCallback } from 'react'
import { Download, MessageSquare, Star, User, Calendar, ChevronDown, ChevronUp } from 'lucide-react'
import { apiService } from '../services/api'
import { FeedbackSummaryResponse, FeedbackItem } from '../types'

interface AdminFeedbackPanelProps {
  accessLevel: 'visionary_expert' | 'admin';
}

const AdminFeedbackPanel: React.FC<AdminFeedbackPanelProps> = ({ accessLevel }) => {
  const [feedbackData, setFeedbackData] = useState<FeedbackSummaryResponse | null>(null);
  const [allFeedbacks, setAllFeedbacks] = useState<FeedbackItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

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
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderStars = (rating?: number) => {
    if (!rating) return <span className="text-gray-400">No rating</span>;
    
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
        <span className="ml-1 text-sm font-medium">{rating}/5</span>
      </div>
    );
  };

  useEffect(() => {
    loadFeedbackSummary();
  }, [loadFeedbackSummary]);

  if (accessLevel !== 'admin') {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50 to-violet-100">
        <div className="text-center text-gray-600">
          <User className="w-12 h-12 mx-auto mb-2 text-gray-400" />
          <p>Admin access required</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50 to-violet-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading feedback data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50 to-violet-100">
        <div className="text-center text-red-600">
          <MessageSquare className="w-12 h-12 mx-auto mb-2" />
          <p className="font-medium">Error loading feedback</p>
          <p className="text-sm text-gray-600 mt-1">{error}</p>
          <button 
            onClick={loadFeedbackSummary}
            className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-gradient-to-br from-slate-50 via-purple-50 to-violet-100 p-4 sm:p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <MessageSquare className="w-8 h-8 text-purple-600" />
              <h1 className="text-2xl font-bold text-gray-900">Feedback Overview</h1>
            </div>
            <button
              onClick={handleExportCSV}
              disabled={isExporting}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="w-4 h-4" />
              <span>{isExporting ? 'Exporting...' : 'Export CSV'}</span>
            </button>
          </div>

          {/* Summary Stats */}
          {feedbackData && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-purple-200/50">
                <div className="text-2xl font-bold text-purple-600">{feedbackData.summary.total_feedback}</div>
                <div className="text-sm text-gray-600">Total Feedback</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-purple-200/50">
                <div className="text-2xl font-bold text-yellow-600">{feedbackData.summary.average_rating.toFixed(1)}</div>
                <div className="text-sm text-gray-600">Average Rating</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-purple-200/50">
                <div className="text-2xl font-bold text-green-600">
                  {(feedbackData.summary.rating_distribution[5] || 0) + (feedbackData.summary.rating_distribution[4] || 0)}
                </div>
                <div className="text-sm text-gray-600">Positive (4-5★)</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-purple-200/50">
                <div className="text-2xl font-bold text-red-600">
                  {(feedbackData.summary.rating_distribution[1] || 0) + (feedbackData.summary.rating_distribution[2] || 0)}
                </div>
                <div className="text-sm text-gray-600">Negative (1-2★)</div>
              </div>
            </div>
          )}
        </div>

        {/* Feedback List */}
        <div className="bg-white/80 backdrop-blur-sm rounded-xl border border-purple-200/50 overflow-hidden">
          <div className="p-4 border-b border-purple-200/50">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center justify-between w-full text-left"
            >
              <h2 className="text-lg font-semibold text-gray-900">Recent Feedback</h2>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">
                  {isExpanded ? 'Collapse' : `Show all (${allFeedbacks.length})`}
                </span>
                {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </div>
            </button>
          </div>

          <div 
            ref={scrollContainerRef}
            className={`transition-all duration-300 ${
              isExpanded ? 'max-h-96 overflow-y-auto' : 'max-h-80'
            }`}
          >
            {allFeedbacks.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No feedback data available</p>
              </div>
            ) : (
              <div className="divide-y divide-purple-200/30">
                {allFeedbacks.slice(0, isExpanded ? allFeedbacks.length : 10).map((feedback) => (
                  <div key={feedback.id} className="p-4 hover:bg-purple-50/50 transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        {renderStars(feedback.rating)}
                        <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full">
                          {feedback.user_type}
                        </span>
                      </div>
                      <div className="flex items-center text-sm text-gray-500">
                        <Calendar className="w-4 h-4 mr-1" />
                        {formatDate(feedback.created_at)}
                      </div>
                    </div>
                    <p className="text-gray-700 text-sm leading-relaxed">{feedback.comment}</p>
                    {feedback.message_id && (
                      <p className="text-xs text-gray-400 mt-2">Message ID: {feedback.message_id}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminFeedbackPanel 