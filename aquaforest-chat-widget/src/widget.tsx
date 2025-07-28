import React from 'react';
import ReactDOM from 'react-dom/client';
import { WidgetContainer } from './components/WidgetContainer';
import { WidgetConfig } from './types';

// Export components for library usage
export { WidgetContainer };
export type { WidgetConfig };

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

// Attach to window for global access
if (typeof window !== 'undefined') {
  (window as any).AquaforestChatWidget = {
    render,
    WidgetContainer
  };
}

export default { render };