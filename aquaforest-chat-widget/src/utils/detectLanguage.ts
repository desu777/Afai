/**
 * Detects language based on URL pathname
 * @returns 'pl' if URL contains '/pl/', otherwise 'en'
 */
export const detectLanguageFromURL = (): 'pl' | 'en' => {
  if (typeof window === 'undefined') {
    return 'en'; // Default to English for SSR
  }
  
  return window.location.pathname.includes('/pl/') ? 'pl' : 'en';
};

export type SupportedLanguage = 'pl' | 'en';