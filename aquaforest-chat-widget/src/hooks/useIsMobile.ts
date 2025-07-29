import { useState, useEffect } from 'react';

/**
 * Custom hook to detect if the user is on a mobile device
 * @param breakpoint - The maximum width in pixels to consider as mobile (default: 768)
 * @returns boolean - true if the device is mobile, false otherwise
 */
export const useIsMobile = (breakpoint: number = 768): boolean => {
  // Initialize with actual value to prevent flash
  const getInitialValue = () => {
    if (typeof window !== 'undefined') {
      return window.matchMedia(`(max-width: ${breakpoint}px)`).matches;
    }
    return false;
  };
  
  const [isMobile, setIsMobile] = useState<boolean>(getInitialValue());

  useEffect(() => {
    // Initial check
    const checkDevice = () => {
      const mediaQuery = window.matchMedia(`(max-width: ${breakpoint}px)`);
      setIsMobile(mediaQuery.matches);
      return mediaQuery;
    };

    // Set initial value
    const mediaQuery = checkDevice();

    // Handler for changes
    const handleChange = (event: MediaQueryListEvent) => {
      setIsMobile(event.matches);
    };

    // Modern browsers use addEventListener
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
    } else {
      // Fallback for older browsers
      mediaQuery.addListener(handleChange);
    }

    // Cleanup
    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleChange);
      } else {
        // Fallback for older browsers
        mediaQuery.removeListener(handleChange);
      }
    };
  }, [breakpoint]);

  return isMobile;
};