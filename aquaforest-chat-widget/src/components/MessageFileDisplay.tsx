import React from 'react';
import { FileText, CheckCircle, Image } from 'lucide-react';

interface MessageFileDisplayProps {
  imageUrl: string;
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
      <div className="af-message-pdf-display">
        <div className="af-pdf-display-content">
          <div className="af-pdf-display-icon">
            <FileText className="af-pdf-file-icon" />
            <CheckCircle className="af-pdf-check-badge" />
          </div>
          <div className="af-pdf-display-info">
            <p className="af-pdf-filename">
              {fileName || 'PDF Document'}
            </p>
            <p className="af-pdf-description">
              ICP Analysis Document {fileSize && `• ${formatFileSize(fileSize)}`}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // For images, show the actual image with metadata overlay
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