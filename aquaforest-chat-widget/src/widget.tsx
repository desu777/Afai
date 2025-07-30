import React from 'react';
import ReactDOM from 'react-dom/client';
import { WidgetContainer } from './components/WidgetContainer';
import type { WidgetConfig } from './types';

// Global function to render widget
interface RenderOptions extends WidgetConfig {
  containerId: string;
}

const render = (options: RenderOptions) => {
  const { containerId, ...widgetProps } = options;
  
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Container with id "${containerId}" not found`);
    return;
  }

  const root = ReactDOM.createRoot(container);
  root.render(
    <React.StrictMode>
      <WidgetContainer {...widgetProps} />
    </React.StrictMode>
  );
};

// Export for ES modules
export { render, WidgetContainer };
export type { WidgetConfig };

// IIFE for guaranteed global assignment - ELITE PATTERN
(function() {
  if (typeof window !== 'undefined') {
    (window as any).AquaforestChatWidget = { render, WidgetContainer };
  }
  if (typeof global !== 'undefined') {
    (global as any).AquaforestChatWidget = { render, WidgetContainer };
  }
})();

// Default export for UMD compatibility
export default { render, WidgetContainer };