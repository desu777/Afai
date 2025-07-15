import { FileText, CheckCircle } from 'lucide-react';

interface ImagePreviewProps {
  imagePreview: string | null;
  onRemove: () => void;
  isPDF?: boolean;
  fileName?: string;
  fileType?: 'image' | 'pdf' | null;
  fileSize?: number;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ 
  imagePreview, 
  onRemove, 
  isPDF = false, 
  fileName = '',
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
  if (!imagePreview && !isPDF) return null;

  return (
    <div className="mb-4 relative">
      <div className="relative inline-block">
        {isPDF ? (
          // PDF Preview with confirmation
          <div className="flex items-center space-x-3 p-4 bg-gradient-to-r from-purple-50 to-violet-50 border border-purple-200/60 rounded-xl shadow-lg max-w-sm">
            <div className="relative">
              <FileText className="w-10 h-10 text-purple-600" />
              <CheckCircle className="absolute -top-1 -right-1 w-5 h-5 text-green-500 bg-white rounded-full" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-purple-900 truncate">
                {fileName || 'PDF Document'}
              </p>
              <p className="text-xs text-purple-600 mb-1">
                ICP Analysis Document {fileSize && `• ${formatFileSize(fileSize)}`}
              </p>
              <div className="flex items-center text-xs text-green-600">
                <CheckCircle className="w-3 h-3 mr-1" />
                <span>Successfully uploaded</span>
              </div>
            </div>
          </div>
        ) : (
          // Image Preview with confirmation
          <div className="relative">
            <img
              src={imagePreview || ''}
              alt="Selected image"
              className="max-w-xs max-h-40 rounded-xl shadow-lg border border-purple-200/60"
            />
            <div className="absolute bottom-2 right-2 bg-white/90 backdrop-blur-sm rounded-full p-1 shadow-md">
              <CheckCircle className="w-4 h-4 text-green-500" />
            </div>
            <div className="absolute bottom-2 left-2 bg-white/90 backdrop-blur-sm rounded-md px-2 py-1 shadow-md">
              <span className="text-xs text-green-600 font-medium">Uploaded</span>
            </div>
          </div>
        )}
        <button
          onClick={onRemove}
          className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center text-xs font-bold shadow-lg transition-all duration-200 hover:scale-110"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default ImagePreview; 