import { useMemo } from 'react';
import { detectLanguageFromURL, type SupportedLanguage } from '../utils/detectLanguage';
import { translations, type Translation } from '../i18n/translations';

export interface UseTranslationReturn {
  t: Translation;
  language: SupportedLanguage;
}

/**
 * Hook for accessing translations based on URL language detection
 * @returns Object with translations (t) and current language
 */
export const useTranslation = (): UseTranslationReturn => {
  const language = useMemo(() => detectLanguageFromURL(), []);
  
  return {
    t: translations[language],
    language
  };
};