interface ImagePreviewProps {
  imagePreview: string | null;
  onRemove: () => void;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ imagePreview, onRemove }) => {
  if (!imagePreview) return null;

  return (
    <div className="mb-4 relative">
      <div className="relative inline-block">
        <img
          src={imagePreview}
          alt="Selected image"
          className="max-w-xs max-h-40 rounded-lg shadow-md border border-purple-200/60"
        />
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