import React from 'react';
import { FileText, CheckCircle } from 'lucide-react';

interface ImagePreviewProps {
  imagePreview: string | null;
  onRemove: () => void;
  isPDF?: boolean;
  fileName?: string;
  fileType?: 'image' | 'pdf' | null;
  fileSize?: number;
}

export const ImagePreview: React.FC<ImagePreviewProps> = ({ 
  imagePreview, 
  onRemove, 
  isPDF = false, 
  fileName = '',
  fileSize,
  fileType
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
  
  // Use fileType or fallback to isPDF check
  const isImage = fileType === 'image' || (!fileType && !isPDF && imagePreview);
  const isPDFFile = fileType === 'pdf' || isPDF;
  
  if (!isImage && !isPDFFile) return null;

  return (
    <div className="af-image-preview">
      <div className="af-image-preview-container">
        {/* Unified confirmation UI for both images and PDFs */}
        <div className="af-pdf-preview">
          <div className="af-pdf-icon-wrapper">
            <FileText className="af-pdf-icon" />
            <CheckCircle className="af-pdf-check" />
          </div>
          <div className="af-pdf-info">
            <p className="af-pdf-title">
              {fileName || (isImage ? 'Image' : 'PDF Document')}
            </p>
            <p className="af-pdf-subtitle">
              {fileSize && formatFileSize(fileSize)}
            </p>
            <div className="af-pdf-status">
              <CheckCircle className="af-pdf-status-icon" />
              <span>Uploaded successfully</span>
            </div>
          </div>
        </div>
        <button
          onClick={onRemove}
          className="af-preview-remove"
        >
          ×
        </button>
      </div>
    </div>
  );
};