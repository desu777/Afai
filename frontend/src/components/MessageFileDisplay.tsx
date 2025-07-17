import { FileText, CheckCircle, Image } from 'lucide-react';

interface MessageFileDisplayProps {
  imageUrl: string;
  fileName?: string;
  fileType?: 'image' | 'pdf';
  fileSize?: number;
}

const MessageFileDisplay: React.FC<MessageFileDisplayProps> = ({ 
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
      <div className="mb-3 inline-block max-w-sm">
        <div className="flex items-center space-x-3 p-3 bg-gradient-to-r from-purple-50 to-violet-50 border border-purple-200/60 rounded-lg shadow-sm">
          <div className="relative">
            <FileText className="w-8 h-8 text-purple-600" />
            <CheckCircle className="absolute -top-1 -right-1 w-4 h-4 text-green-500 bg-white rounded-full" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-purple-900 truncate">
              {fileName || 'PDF Document'}
            </p>
            <p className="text-xs text-purple-600">
              ICP Analysis Document {fileSize && `• ${formatFileSize(fileSize)}`}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // For images, show the actual image with metadata overlay
  return (
    <div className="mb-3 inline-block">
      <div className="relative">
        <img
          src={imageUrl}
          alt={fileName || "Uploaded image"}
          className="max-w-xs max-h-48 rounded-lg shadow-sm border border-purple-200/60"
        />
        {/* Metadata overlay */}
        <div className="absolute bottom-2 left-2 bg-white/90 backdrop-blur-sm rounded-md px-2 py-1 shadow-sm">
          <div className="flex items-center space-x-1">
            <Image className="w-3 h-3 text-purple-600" />
            <span className="text-xs text-purple-700 font-medium">
              {fileName || 'Image'}
            </span>
            {fileSize && (
              <span className="text-xs text-purple-600">
                • {formatFileSize(fileSize)}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageFileDisplay;