import React from 'react';
import { FileText, CheckCircle, Image } from 'lucide-react';

interface MessageFileDisplayProps {
  imageUrl?: string;
  fileName?: string;
  fileType?: 'image' | 'pdf';
  fileSize?: number;
}

export const MessageFileDisplay: React.FC<MessageFileDisplayProps> = ({ 
  imageUrl, 
  fileName = '',
  fileType,
  fileSize 
}) => {
  // Helper function to format file size
  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return '';
    const kb = bytes / 1024;
    const mb = kb / 1024;
    if (mb > 1) {
      return `${mb.toFixed(1)} MB`;
    } else {
      return `${kb.toFixed(1)} KB`;
    }
  };

  if (fileType === 'pdf') {
    return (
      <div className="af-pdf-preview">
        <div className="af-pdf-icon-wrapper">
          <FileText className="af-pdf-icon" />
          <CheckCircle className="af-pdf-check" />
        </div>
        <div className="af-pdf-info">
          <p className="af-pdf-title">
            {fileName || 'PDF Document'}
          </p>
          <p className="af-pdf-subtitle">
            {fileSize && formatFileSize(fileSize)}
          </p>
          <div className="af-pdf-status">
            <CheckCircle className="af-pdf-status-icon" />
            <span>Attached</span>
          </div>
        </div>
      </div>
    );
  }

  // For images, show the actual image with metadata overlay (only if imageUrl exists)
  if (!imageUrl) {
    return null; // Don't render anything if no imageUrl for images
  }
  
  return (
    <div className="af-message-image-display">
      <div className="af-image-display-wrapper">
        <img
          src={imageUrl}
          alt={fileName || "Uploaded image"}
          className="af-display-image"
        />
        {/* Metadata overlay */}
        <div className="af-image-metadata">
          <div className="af-image-metadata-content">
            <Image className="af-image-icon" />
            <span className="af-image-filename">
              {fileName || 'Image'}
            </span>
            {fileSize && (
              <span className="af-image-size">
                • {formatFileSize(fileSize)}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};