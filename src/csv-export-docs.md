# CSV Export Endpoints

## Analytics Export

### GET `/analytics/export/csv`
Export analytics data to CSV file.

**Query Parameters:**
- `start_date` (optional) - Filter from date (format: YYYY-MM-DD)
- `end_date` (optional) - Filter to date (format: YYYY-MM-DD)

**Example:**
```bash
# Export all analytics
curl -O http://localhost:2103/analytics/export/csv

# Export analytics for specific date range
curl -O "http://localhost:2103/analytics/export/csv?start_date=2024-01-01&end_date=2024-12-31"
```

**CSV Columns:**
- ID
- Query
- Language
- Intent
- Intent Confidence
- Business Interpretation
- Business Corrections
- Optimized Queries
- Pinecone Results Count
- Top Results
- Filter Decision
- Filtered Count
- Confidence Score
- Confidence Reasoning
- Final Response (truncated to 100 chars)
- Execution Time
- Node Timings (JSON)
- Escalated
- Created At

## Feedback Export

### GET `/feedback/export/csv`
Export feedback data to CSV file.

**Query Parameters:**
- `start_date` (optional) - Filter from date (format: YYYY-MM-DD)
- `end_date` (optional) - Filter to date (format: YYYY-MM-DD)

**Example:**
```bash
# Export all feedback
curl -O http://localhost:2103/feedback/export/csv

# Export feedback for specific date range
curl -O "http://localhost:2103/feedback/export/csv?start_date=2024-01-01&end_date=2024-12-31"
```

**CSV Columns:**
- ID
- Message ID
- User Query
- Response (truncated to 100 chars)
- Rating
- Comment
- User Type
- Created At

## Integration with Frontend

### React Example - Download Analytics
```typescript
const downloadAnalytics = async () => {
  const response = await fetch('http://localhost:2103/analytics/export/csv');
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `analytics_${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
};
```

### React Example - Download Feedback
```typescript
const downloadFeedback = async (startDate?: string, endDate?: string) => {
  let url = 'http://localhost:2103/feedback/export/csv';
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (params.toString()) url += '?' + params.toString();
  
  const response = await fetch(url);
  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = `feedback_${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
};
```

### Admin Dashboard Component
```typescript
// Add to admin dashboard
{accessLevel === 'admin' && (
  <div className="export-buttons">
    <button onClick={downloadAnalytics}>
      📊 Export Analytics CSV
    </button>
    <button onClick={() => downloadFeedback()}>
      💬 Export Feedback CSV
    </button>
  </div>
)}
```

## Notes

- CSV files are UTF-8 encoded with BOM for Excel compatibility
- Long text fields (responses) are truncated to 100 characters
- JSON fields (like node_timings) are exported as strings
- File names include timestamp for easy organization
- No authentication required (add if needed)
