import { useState, useEffect, useCallback } from 'react'
import { Download, Clock, Brain, ChevronRight, Activity, TrendingUp, X, Copy, Eye } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { apiService } from '../services/api'
import { AnalyticsSummaryResponse, AnalyticsItem, TrendDataPoint } from '../types'

interface AdminAnalyticsPanelProps {
  accessLevel: 'visionary_expert' | 'admin';
}

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
}

interface DetailModalProps {
  item: AnalyticsItem | null;
  isOpen: boolean;
  onClose: () => void;
}

interface TrendChartProps {
  data: TrendDataPoint[];
  isLoading?: boolean;
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

const TrendChart: React.FC<TrendChartProps> = ({ data, isLoading = false }) => {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('pl-PL', { month: '2-digit', day: '2-digit' });
  };

  const formatChartData = (data: TrendDataPoint[]) => {
    return data.map(point => ({
      ...point,
      displayDate: formatDate(point.date)
    }));
  };

  if (isLoading) {
    return (
      <div className="bg-white p-4 sm:p-6 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base sm:text-lg font-light text-gray-900">Query Trend (30 days)</h2>
        </div>
        <div className="h-48 sm:h-64 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-brand-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-4 sm:p-6 rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base sm:text-lg font-light text-gray-900">Query Trend (30 days)</h2>
        <TrendingUp className="w-5 h-5 text-gray-400" />
      </div>
      
      <div className="h-48 sm:h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={formatChartData(data)}
            margin={{
              top: 5,
              right: 5,
              left: 5,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis 
              dataKey="displayDate" 
              stroke="#9ca3af"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              stroke="#9ca3af"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              }}
              formatter={(value: number) => [value, 'Queries']}
              labelFormatter={(label: string) => `Date: ${label}`}
            />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#47154C"
              strokeWidth={2}
              dot={{ fill: '#47154C', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#47154C', strokeWidth: 2, fill: 'white' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const DetailModal: React.FC<DetailModalProps> = ({ item, isOpen, onClose }) => {
  if (!isOpen || !item) return null;

  const handleCopyResponse = async () => {
    if (item.final_response) {
      await navigator.clipboard.writeText(item.final_response);
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

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Query Details</h3>
            <p className="text-sm text-gray-500 mt-1">{formatDate(item.created_at)}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content - scrollable */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
          {/* Query Section */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">User Query</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-900 whitespace-pre-wrap">{item.user_query}</p>
            </div>
          </div>

          {/* Response Section */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-700">AI Response</h4>
              <button
                onClick={handleCopyResponse}
                className="flex items-center space-x-1 text-sm text-brand-600 hover:text-brand-700"
              >
                <Copy className="w-4 h-4" />
                <span>Copy</span>
              </button>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
              <p className="text-sm text-gray-900 whitespace-pre-wrap">
                {item.final_response || 'No response available'}
              </p>
            </div>
          </div>

          {/* Metrics Grid */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Metrics</h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600">Intent</p>
                <p className="text-sm font-medium text-gray-900 mt-1">
                  {item.intent_detector_decision}
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600">Confidence</p>
                <p className="text-sm font-medium text-gray-900 mt-1">
                  {item.intent_confidence != null 
                    ? `${(item.intent_confidence * 100).toFixed(0)}%`
                    : 'N/A'}
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600">Response Time</p>
                <p className="text-sm font-medium text-gray-900 mt-1">
                  {item.total_execution_time != null 
                    ? `${item.total_execution_time.toFixed(3)}s`
                    : 'N/A'}
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600">Products Found</p>
                <p className="text-sm font-medium text-gray-900 mt-1">
                  {item.pinecone_results_count || 0}
                </p>
              </div>
            </div>
          </div>

          {/* Technical Details */}
          {item.business_corrections && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Business Corrections</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-900 whitespace-pre-wrap">
                  {item.business_corrections}
                </p>
              </div>
            </div>
          )}

          {/* Node Timings */}
          {item.node_timings && Object.keys(item.node_timings).length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Processing Times</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="space-y-2">
                  {Object.entries(item.node_timings).map(([node, time]) => (
                    <div key={node} className="flex justify-between text-sm">
                      <span className="text-gray-600">{node}</span>
                      <span className="text-gray-900 font-medium">{time}s</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const AdminAnalyticsPanel: React.FC<AdminAnalyticsPanelProps> = ({ accessLevel }) => {
  const [summaryData, setSummaryData] = useState<AnalyticsSummaryResponse | null>(null);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsItem[]>([]);
  const [trendData, setTrendData] = useState<TrendDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isTrendLoading, setIsTrendLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [selectedItem, setSelectedItem] = useState<AnalyticsItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadAnalyticsSummary = useCallback(async () => {
    try {
      setIsLoading(true);
      setIsTrendLoading(true);
      setError(null);
      
      const [summaryResponse, dataResponse, trendResponse] = await Promise.all([
        apiService.getAnalyticsSummary(),
        apiService.getAnalyticsData({ limit: 10 }),
        apiService.getDailyTrend(30)
      ]);
      
      setSummaryData(summaryResponse);
      setAnalyticsData(dataResponse.data || []);
      setTrendData(trendResponse.data || []);
      
      if (import.meta.env.VITE_TEST_ENV === 'true') {
        console.log('✅ [AdminAnalytics] Data loaded:', { summaryResponse, dataResponse, trendResponse });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load analytics data';
      setError(errorMessage);
      console.error('❌ [AdminAnalytics] Error loading data:', err);
    } finally {
      setIsLoading(false);
      setIsTrendLoading(false);
    }
  }, []);

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
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatExecutionTime = (time: number | undefined | null) => {
    if (time == null) return '0.00s';
    return `${time.toFixed(2)}s`;
  };

  const getConfidenceColor = (confidence: number | undefined | null) => {
    if (confidence == null) return 'text-gray-600 bg-gray-50';
    if (confidence >= 0.8) return 'text-green-600 bg-green-50';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const handleViewDetails = (item: AnalyticsItem) => {
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  useEffect(() => {
    loadAnalyticsSummary();
    const interval = setInterval(loadAnalyticsSummary, 60000);
    return () => clearInterval(interval);
  }, [loadAnalyticsSummary]);

  if (isLoading) {
    return (
      <div className="h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
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
            onClick={loadAnalyticsSummary}
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
      <div className="bg-white border-b border-gray-200 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 sm:space-x-4">
              <h1 className="text-lg sm:text-xl font-light text-gray-900">Analytics</h1>
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
          {summaryData && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
              <MetricCard
                title="Total Requests"
                value={summaryData.summary?.total_queries?.toLocaleString() || '0'}
                icon={<Activity className="w-5 h-5 sm:w-6 sm:h-6" />}
                subtitle="All time"
              />
              <MetricCard
                title="Avg Response"
                value={`${summaryData.summary?.average_execution_time?.toFixed(2) || '0.00'}s`}
                icon={<Clock className="w-5 h-5 sm:w-6 sm:h-6" />}
                subtitle="Per request"
              />
              <MetricCard
                title="Escalation"
                value={`${summaryData.summary?.escalation_rate || 0}%`}
                icon={<TrendingUp className="w-5 h-5 sm:w-6 sm:h-6" />}
                subtitle="Complex queries"
              />
              <MetricCard
                title="High Confidence"
                value={summaryData.summary?.confidence_distribution?.high_confidence || 0}
                icon={<Brain className="w-5 h-5 sm:w-6 sm:h-6" />}
                subtitle="Responses"
              />
            </div>
          )}

          {/* Trend Chart */}
          <div className="mb-6 sm:mb-8">
            <TrendChart data={trendData} isLoading={isTrendLoading} />
          </div>

          {/* Intent Distribution */}
          {summaryData?.summary?.intent_distribution && (
            <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 mb-6 sm:mb-8">
              <h2 className="text-base sm:text-lg font-light text-gray-900 mb-4">Intent Distribution</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
                {Object.entries(summaryData.summary.intent_distribution).map(([intent, count]) => (
                  <div key={intent} className="text-center">
                    <p className="text-xs sm:text-sm text-gray-600 capitalize">{intent.replace('_', ' ')}</p>
                    <p className="text-lg sm:text-xl font-light text-gray-900 mt-1">{count || 0}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Activity - Desktop Table */}
          <div className="bg-white rounded-lg border border-gray-200 hidden sm:block">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-light text-gray-900">Recent Activity (Last 10)</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Query
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Intent
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Confidence
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {analyticsData.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatDate(item.created_at)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <p className="truncate max-w-xs" title={item.user_query}>
                          {item.user_query}
                        </p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                          {item.intent_detector_decision}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(item.intent_confidence)}`}>
                          {item.intent_confidence != null ? (item.intent_confidence * 100).toFixed(0) + '%' : '-%'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatExecutionTime(item.total_execution_time)}
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

          {/* Recent Activity - Mobile Cards */}
          <div className="sm:hidden space-y-4">
            <h2 className="text-base font-light text-gray-900 mb-3">Recent Activity</h2>
            {analyticsData.map((item) => (
              <div key={item.id} className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-500">{formatDate(item.created_at)}</p>
                    <p className="text-sm text-gray-900 mt-1 line-clamp-2">{item.user_query}</p>
                  </div>
                  <button
                    onClick={() => handleViewDetails(item)}
                    className="ml-2 p-1 text-brand-600"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
                <div className="flex items-center space-x-2 mt-3">
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                    {item.intent_detector_decision}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(item.intent_confidence)}`}>
                    {item.intent_confidence != null ? (item.intent_confidence * 100).toFixed(0) + '%' : '-%'}
                  </span>
                  <span className="text-xs text-gray-600">
                    {formatExecutionTime(item.total_execution_time)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      <DetailModal 
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

export default AdminAnalyticsPanel;