import { useState, useEffect } from 'react'
import { Eye, EyeOff } from 'lucide-react'

interface SplashScreenProps {
  onAuthenticate: (accessLevel: 'visionary_expert' | 'admin') => void;
}

const SplashScreen: React.FC<SplashScreenProps> = ({ onAuthenticate }) => {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Check for saved access code on component mount
  useEffect(() => {
    const checkSavedAccess = () => {
      try {
        const savedAccess = localStorage.getItem('af_access_code');
        if (savedAccess) {
          const { timestamp, level } = JSON.parse(savedAccess);
          const now = Date.now();
          const twentyFourHours = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
          
          // Check if saved code is still valid (less than 24 hours old)
          if (now - timestamp < twentyFourHours) {
            // Auto-authenticate with saved credentials
            setIsLoading(true);
            setTimeout(() => {
              onAuthenticate(level);
            }, 500); // Small delay for smooth UX
            return;
          } else {
            // Remove expired code
            localStorage.removeItem('af_access_code');
          }
        }
      } catch (error) {
        // Clear corrupted data
        localStorage.removeItem('af_access_code');
      }
    };

    checkSavedAccess();
  }, [onAuthenticate]);

  const saveAccessCode = (code: string, level: 'visionary_expert' | 'admin') => {
    try {
      const accessData = {
        code,
        level,
        timestamp: Date.now()
      };
      localStorage.setItem('af_access_code', JSON.stringify(accessData));
    } catch (error) {
      console.warn('Failed to save access code to localStorage');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Simulate API delay
    setTimeout(() => {
      const testAccess = import.meta.env.VITE_TEST_ACCESS;
      const adminAccess = import.meta.env.VITE_ADMIN_ACCESS;

      if (password === testAccess) {
        saveAccessCode(password, 'visionary_expert');
        onAuthenticate('visionary_expert');
      } else if (password === adminAccess) {
        saveAccessCode(password, 'admin');
        onAuthenticate('admin');
      } else {
        setError('Invalid access code. Please try again.');
      }
      setIsLoading(false);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-lg bg-brand-600 shadow-lg mb-8">
            <div className="circle">
              <div className="wave"></div>
            </div>
          </div>
          
          {/* Animated Title */}
          <div className="mb-4">
            <svg viewBox="0 0 200 50" className="w-full h-16 max-w-[320px] mx-auto">
              <defs>
                <linearGradient id="splash-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style={{stopColor: '#9333ea'}} />
                  <stop offset="50%" style={{stopColor: '#7c3aed'}} />
                  <stop offset="100%" style={{stopColor: '#5b21b6'}} />
                </linearGradient>
                <pattern id="splash-wave" x="0" y="-0.5" width="100%" height="100%" patternUnits="userSpaceOnUse">
                  <path d="M-40 25 Q-30 20 -20 25 T0 25 T20 25 T40 25 T60 25 T80 25 T100 25 T120 25 T140 25 T160 25 T180 25 T200 25 T220 25 V50 H-40z" fill="url(#splash-gradient)">
                    <animateTransform
                      attributeName="transform"
                      begin="0s"
                      dur="3s"
                      type="translate"
                      from="0,0"
                      to="40,0"
                      repeatCount="indefinite" />
                  </path>
                </pattern>
              </defs>
              <text textAnchor="middle" x="100" y="35" fontSize="28" fontWeight="bold" fill="#1f2937" fillOpacity="0.1">Afai by Aquaforest</text>
              <text textAnchor="middle" x="100" y="35" fontSize="28" fontWeight="bold" fill="url(#splash-wave)" fillOpacity="1">Afai by Aquaforest</text>
            </svg>
          </div>
          
          <p className="text-body text-lg md:text-xl text-gray-600 font-medium leading-relaxed">
            As Far As I know, I'm here to help you make your reef even better.
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-lg p-8 shadow-md border border-gray-200">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Access Code
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-lg focus:border-brand-600 focus:ring-2 focus:ring-brand-600/20 outline-none transition-all duration-200 font-medium"
                  placeholder="Enter your access code"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-gray-100 rounded-lg transition-colors"
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5 text-gray-500" />
                  ) : (
                    <Eye className="w-5 h-5 text-gray-500" />
                  )}
                </button>
              </div>
              {error && (
                <p className="mt-2 text-sm text-red-600 font-medium">{error}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={!password.trim() || isLoading}
              className="w-full bg-brand-600 hover:bg-brand-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg shadow-sm transition-colors duration-200"
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Authenticating...</span>
                </div>
              ) : (
                'Access Afai'
              )}
            </button>
          </form>
        </div>

        {/* Footer with Logo */}
        <div className="text-center mt-12 space-y-4">
          <img 
            src="/aquaforest_logo.png" 
            alt="Aquaforest" 
            className="h-8 mx-auto opacity-60 hover:opacity-80 transition-opacity"
          />
          <div className="space-y-2">
            <p className="text-xs text-gray-500 font-medium">
              Aquaforest AI Assistant • Secure Access Required
            </p>
            <p className="text-xs text-gray-400 font-medium">
              Access code will be remembered for 24 hours
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SplashScreen; 