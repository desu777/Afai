import { useState, useEffect, useRef, useCallback } from 'react'
import { Download, BarChart3, User, Clock, Brain, Search, ChevronDown, ChevronUp, Target } from 'lucide-react'
import { apiService } from '../services/api'
import { AnalyticsSummaryResponse, AnalyticsItem } from '../types'

interface AdminAnalyticsPanelProps {
  accessLevel: 'test' | 'admin';
}

const AdminAnalyticsPanel: React.FC<AdminAnalyticsPanelProps> = ({ accessLevel }) => {
  const [summaryData, setSummaryData] = useState<AnalyticsSummaryResponse | null>(null);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const loadAnalyticsSummary = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const [summaryResponse, dataResponse] = await Promise.all([
        apiService.getAnalyticsSummary(),
        apiService.getAnalyticsData({ limit: 10 })
      ]);
      
      setSummaryData(summaryResponse);
      setAnalyticsData(dataResponse.data || []);
      
      if (import.meta.env.VITE_TEST_ENV === 'true') {
        console.log('✅ [AdminAnalytics] Data loaded:', { summaryResponse, dataResponse });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load analytics data';
      setError(errorMessage);
      console.error('❌ [AdminAnalytics] Error loading data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadMoreData = useCallback(async () => {
    if (loadingMore) return;
    
    try {
      setLoadingMore(true);
      const response = await apiService.getAnalyticsData({ 
        limit: analyticsData.length + 10 
      });
      setAnalyticsData(response.data || []);
    } catch (err) {
      console.error('❌ [AdminAnalytics] Error loading more data:', err);
    } finally {
      setLoadingMore(false);
    }
  }, [analyticsData.length, loadingMore]);

  const handleExportCSV = async () => {
    try {
      setIsExporting(true);
      const blob = await apiService.exportAnalyticsCSV();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      if (import.meta.env.VITE_TEST_ENV === 'true') {
        console.log('✅ [AdminAnalytics] CSV exported successfully');
      }
    } catch (err) {
      console.error('❌ [AdminAnalytics] Export failed:', err);
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

  const formatExecutionTime = (time: number) => {
    return `${time.toFixed(3)}s`;
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50';
    if (confidence >= 0.5) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const truncateText = (text: string, maxLength: number = 50) => {
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  };

  useEffect(() => {
    loadAnalyticsSummary();
  }, [loadAnalyticsSummary]);

  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;
    if (!scrollContainer || !isExpanded) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
      if (scrollTop + clientHeight >= scrollHeight - 10) {
        loadMoreData();
      }
    };

    scrollContainer.addEventListener('scroll', handleScroll);
    return () => scrollContainer.removeEventListener('scroll', handleScroll);
  }, [isExpanded, loadMoreData]);

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
          <p className="text-gray-600">Loading analytics data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50 to-violet-100">
        <div className="text-center text-red-600">
          <BarChart3 className="w-12 h-12 mx-auto mb-2" />
          <p className="font-medium">Error loading analytics</p>
          <p className="text-sm text-gray-600 mt-1">{error}</p>
          <button 
            onClick={loadAnalyticsSummary}
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
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <BarChart3 className="w-8 h-8 text-purple-600" />
              <h1 className="text-2xl font-bold text-gray-900">Analytics Overview</h1>
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
          {summaryData && (
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-purple-200/50">
                <div className="text-2xl font-bold text-purple-600">{summaryData.summary.total_queries}</div>
                <div className="text-sm text-gray-600">Total Queries</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-purple-200/50">
                <div className="text-2xl font-bold text-blue-600">{summaryData.summary.average_execution_time.toFixed(3)}s</div>
                <div className="text-sm text-gray-600">Avg Response Time</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-purple-200/50">
                <div className="text-2xl font-bold text-green-600">{summaryData.summary.confidence_distribution.high_confidence}</div>
                <div className="text-sm text-gray-600">High Confidence</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-purple-200/50">
                <div className="text-2xl font-bold text-red-600">{summaryData.summary.escalation_rate.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Escalation Rate</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-purple-200/50">
                <div className="text-2xl font-bold text-orange-600">
                  {Object.keys(summaryData.summary.language_distribution).length}
                </div>
                <div className="text-sm text-gray-600">Languages</div>
              </div>
            </div>
          )}
        </div>

        {/* Analytics Table */}
        <div className="bg-white/80 backdrop-blur-sm rounded-xl border border-purple-200/50 overflow-hidden">
          <div className="p-4 border-b border-purple-200/50">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center justify-between w-full text-left"
            >
              <h2 className="text-lg font-semibold text-gray-900">Recent Analytics</h2>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">
                  {isExpanded ? 'Collapse' : `Show all (${analyticsData.length})`}
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
            {analyticsData.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <BarChart3 className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No analytics data available</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-purple-50/50 text-gray-700">
                    <tr>
                      <th className="px-4 py-3 text-left font-medium">Query</th>
                      <th className="px-4 py-3 text-left font-medium">Intent</th>
                      <th className="px-4 py-3 text-left font-medium">Confidence</th>
                      <th className="px-4 py-3 text-left font-medium">Time</th>
                      <th className="px-4 py-3 text-left font-medium">Results</th>
                      <th className="px-4 py-3 text-left font-medium">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-purple-200/30">
                    {analyticsData.slice(0, isExpanded ? analyticsData.length : 10).map((item) => (
                      <tr key={item.id} className="hover:bg-purple-50/30 transition-colors">
                        <td className="px-4 py-3">
                          <div className="max-w-xs">
                            <p className="text-gray-900 font-medium" title={item.user_query}>
                              {truncateText(item.user_query, 40)}
                            </p>
                            <p className="text-xs text-gray-500">{item.detected_language}</p>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center space-x-2">
                            <Brain className="w-4 h-4 text-purple-500" />
                            <span className="text-gray-700">{item.intent_detector_decision}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(item.confidence_score)}`}>
                            {(item.confidence_score * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center space-x-1">
                            <Clock className="w-4 h-4 text-gray-400" />
                            <span>{formatExecutionTime(item.total_execution_time)}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center space-x-1">
                            <Search className="w-4 h-4 text-gray-400" />
                            <span>{item.pinecone_results_count}</span>
                            {item.escalated && (
                              <div title="Escalated">
                                <Target className="w-4 h-4 text-red-500 ml-2" />
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-gray-500">
                          {formatDate(item.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {loadingMore && (
                  <div className="p-4 text-center">
                    <div className="inline-flex items-center space-x-2 text-sm text-gray-500">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                      <span>Loading more...</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminAnalyticsPanel 