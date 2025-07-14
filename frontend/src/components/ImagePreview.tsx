import { FileText } from 'lucide-react';

interface ImagePreviewProps {
  imagePreview: string | null;
  onRemove: () => void;
  isPDF?: boolean;
  fileName?: string;
  fileType?: 'image' | 'pdf' | null;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ 
  imagePreview, 
  onRemove, 
  isPDF = false, 
  fileName = '',
  fileType 
}) => {
  if (!imagePreview && !isPDF) return null;

  return (
    <div className="mb-4 relative">
      <div className="relative inline-block">
        {isPDF ? (
          // PDF Preview
          <div className="flex items-center space-x-3 p-3 bg-purple-50 border border-purple-200/60 rounded-lg shadow-md max-w-xs">
            <FileText className="w-8 h-8 text-purple-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-purple-900 truncate">
                {fileName || 'PDF Document'}
              </p>
              <p className="text-xs text-purple-600">
                ICP Analysis Document
              </p>
            </div>
          </div>
        ) : (
          // Image Preview
          <img
            src={imagePreview}
            alt="Selected image"
            className="max-w-xs max-h-40 rounded-lg shadow-md border border-purple-200/60"
          />
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