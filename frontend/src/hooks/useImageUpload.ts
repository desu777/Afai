import { useState, useEffect } from 'react';

interface UseImageUploadOptions {
  selectedImage?: File | null;
  onImageSelect?: (image: File | null) => void;
}

export const useImageUpload = (options: UseImageUploadOptions = {}) => {
  const { selectedImage, onImageSelect } = options;
  
  const [selectedImageState, setSelectedImageState] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [fileType, setFileType] = useState<'image' | 'pdf' | null>(null);

  // Synchronizacja z propsami z parent component
  useEffect(() => {
    if (selectedImage !== selectedImageState) {
      setSelectedImageState(selectedImage || null);
      
      // Jeśli parent przekazał plik, utwórz podgląd
      if (selectedImage) {
        const fileType = selectedImage.type.startsWith('image/') ? 'image' : 'pdf';
        setFileType(fileType);
        
        if (fileType === 'image') {
          const reader = new FileReader();
          reader.onload = () => {
            setImagePreview(reader.result as string);
          };
          reader.readAsDataURL(selectedImage);
        } else if (fileType === 'pdf') {
          // For PDFs, we'll show a placeholder preview
          setImagePreview(null);
        }
      } else {
        setImagePreview(null);
        setFileType(null);
      }
    }
  }, [selectedImage, selectedImageState]);

  // Funkcja konwersji pliku na base64 data URL
  const convertFileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  // Funkcja obsługi wyboru pliku (image/PDF)
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Determine file type
      const fileType = file.type.startsWith('image/') ? 'image' : 
                       file.type === 'application/pdf' ? 'pdf' : null;
      
      if (!fileType) {
        console.error('Unsupported file type:', file.type);
        return;
      }
      
      setSelectedImageState(file);
      setFileType(fileType);
      
      // Utworzenie podglądu
      if (fileType === 'image') {
        const reader = new FileReader();
        reader.onload = () => {
          setImagePreview(reader.result as string);
        };
        reader.readAsDataURL(file);
      } else if (fileType === 'pdf') {
        // For PDFs, we'll show a placeholder
        setImagePreview(null);
      }
      
      // Przekazanie do parent component
      if (onImageSelect) {
        onImageSelect(file);
      }
    }
  };

  // Funkcja usuwania pliku
  const removeImage = () => {
    setSelectedImageState(null);
    setImagePreview(null);
    setFileType(null);
    
    // Przekazanie do parent component
    if (onImageSelect) {
      onImageSelect(null);
    }
  };

  // Check if selected file is PDF
  const isPDF = fileType === 'pdf';
  const isImage = fileType === 'image';

  return {
    selectedImageState,
    imagePreview,
    handleImageSelect,
    removeImage,
    convertFileToBase64,
    fileType,
    isPDF,
    isImage
  };
}; 