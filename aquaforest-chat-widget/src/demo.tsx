import React from 'react';
import ReactDOM from 'react-dom/client';
import { WidgetContainer } from './components/WidgetContainer';

const DemoPage: React.FC = () => {
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f5f5f5',
      padding: '2rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ 
          fontSize: '2.5rem', 
          fontWeight: 'bold',
          color: '#1F2937',
          marginBottom: '1rem'
        }}>
          Aquaforest Chat Widget Demo
        </h1>
        
        <p style={{ 
          fontSize: '1.125rem',
          color: '#6B7280',
          marginBottom: '2rem',
          lineHeight: '1.6'
        }}>
          Test the Aquaforest AI assistant widget. Click the purple button in the bottom right corner to start chatting!
        </p>

        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          marginBottom: '2rem'
        }}>
          <h2 style={{ 
            fontSize: '1.5rem',
            fontWeight: '600',
            marginBottom: '1rem',
            color: '#374151'
          }}>
            Widget Configuration
          </h2>
          
          <pre style={{
            background: '#F3F4F6',
            padding: '1rem',
            borderRadius: '8px',
            overflow: 'auto',
            fontSize: '0.875rem'
          }}>
{`<WidgetContainer 
  apiToken="aquaforest_dev_token_2025"
  apiUrl="http://localhost:2103"
  position="bottom-right"
  theme="aquaforest"
/>`}
          </pre>
        </div>

        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          marginBottom: '2rem'
        }}>
          <h2 style={{ 
            fontSize: '1.5rem',
            fontWeight: '600',
            marginBottom: '1rem',
            color: '#374151'
          }}>
            Test Content
          </h2>
          
          <p style={{ marginBottom: '1rem' }}>
            This is a demo page to test the widget functionality. The widget should appear as a floating button in the bottom right corner.
          </p>
          
          <h3 style={{ 
            fontSize: '1.25rem',
            fontWeight: '600',
            marginTop: '1.5rem',
            marginBottom: '0.5rem',
            color: '#4B5563'
          }}>
            Features to Test:
          </h3>
          
          <ul style={{ 
            listStyle: 'disc',
            paddingLeft: '1.5rem',
            color: '#6B7280',
            lineHeight: '1.8'
          }}>
            <li>Click the floating button to open the chat</li>
            <li>Test the welcome screen with animated seahorse icon</li>
            <li>Send messages and receive AI responses</li>
            <li>Upload images or documents</li>
            <li>Test responsive behavior on different screen sizes</li>
          </ul>
        </div>

        {/* Simulate long page content for scroll testing */}
        <div style={{ height: '150vh', paddingTop: '2rem' }}>
          <p style={{ color: '#9CA3AF' }}>
            Scroll down to test widget positioning...
          </p>
        </div>
      </div>

      {/* Widget Instance */}
      <WidgetContainer 
        apiToken="aquaforest_dev_token_2025"
        apiUrl="http://localhost:2103"
        position="bottom-right"
        theme="aquaforest"
      />
    </div>
  );
};

// Mount demo page
const root = document.getElementById('root');
if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <DemoPage />
    </React.StrictMode>
  );
}