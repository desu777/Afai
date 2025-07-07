import { useState, useEffect } from 'react';

interface UseImageUploadOptions {
  selectedImage?: File | null;
  onImageSelect?: (image: File | null) => void;
}

export const useImageUpload = (options: UseImageUploadOptions = {}) => {
  const { selectedImage, onImageSelect } = options;
  
  const [selectedImageState, setSelectedImageState] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  // Synchronizacja z propsami z parent component
  useEffect(() => {
    if (selectedImage !== selectedImageState) {
      setSelectedImageState(selectedImage || null);
      
      // Jeśli parent przekazał plik, utwórz podgląd
      if (selectedImage) {
        const reader = new FileReader();
        reader.onload = () => {
          setImagePreview(reader.result as string);
        };
        reader.readAsDataURL(selectedImage);
      } else {
        setImagePreview(null);
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

  // Funkcja obsługi wyboru zdjęcia
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImageState(file);
      
      // Utworzenie podglądu
      const reader = new FileReader();
      reader.onload = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      
      // Przekazanie do parent component
      if (onImageSelect) {
        onImageSelect(file);
      }
    }
  };

  // Funkcja usuwania zdjęcia
  const removeImage = () => {
    setSelectedImageState(null);
    setImagePreview(null);
    
    // Przekazanie do parent component
    if (onImageSelect) {
      onImageSelect(null);
    }
  };

  return {
    selectedImageState,
    imagePreview,
    handleImageSelect,
    removeImage,
    convertFileToBase64
  };
}; 