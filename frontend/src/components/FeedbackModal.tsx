import { useState, useEffect } from 'react'
import { X, Send, CheckCircle, Star } from 'lucide-react'
import { apiService } from '../services/api'
import { FeedbackRequest } from '../types'

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  accessLevel: 'test' | 'admin' | 'support';
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({ isOpen, onClose, accessLevel }) => {
  const [comment, setComment] = useState('');
  const [rating, setRating] = useState<number>(0);
  const [hoveredRating, setHoveredRating] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');
  const [isClosing, setIsClosing] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isOpen) {
      // Small delay to ensure smooth opening animation
      const timer = setTimeout(() => {
        setIsAnimating(true);
      }, 10);
      return () => clearTimeout(timer);
    } else {
      setIsAnimating(false);
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!comment.trim()) {
      setError('Please enter your feedback before submitting.');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const feedbackData: FeedbackRequest = {
        comment: comment.trim(),
        rating: rating > 0 ? rating : undefined,
        user_type: accessLevel
      };

      await apiService.submitFeedback(feedbackData);
      
      setIsSuccess(true);
      setComment('');
      setRating(0);
      setHoveredRating(0);
      
      // Auto close after 2 seconds with animation
      setTimeout(() => {
        setIsClosing(true);
                  setTimeout(() => {
            setIsSuccess(false);
            setIsClosing(false);
            setIsAnimating(false);
            onClose();
          }, 300);
      }, 2000);

    } catch (error) {
      console.error('Failed to submit feedback:', error);
      setError('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting && !isClosing) {
      setIsClosing(true);
      setTimeout(() => {
        setComment('');
        setRating(0);
        setHoveredRating(0);
        setError('');
        setIsSuccess(false);
        setIsClosing(false);
        setIsAnimating(false);
        onClose();
      }, 300); // Animation duration
    }
  };

  if (!isOpen && !isClosing) return null;

  return (
    <div className={`fixed inset-0 flex items-center justify-center z-[9999] p-4 transition-all duration-300 ${
      isClosing 
        ? 'bg-black/0 backdrop-blur-none' 
        : isAnimating 
          ? 'bg-black/50 backdrop-blur-sm' 
          : 'bg-black/0 backdrop-blur-none'
    }`}>
      <div className={`bg-white/95 backdrop-blur-md rounded-3xl shadow-2xl border border-purple-200/50 w-full max-w-md mx-auto transform transition-all duration-300 ease-out overflow-visible ${
        isClosing 
          ? 'scale-75 opacity-0 translate-y-8' 
          : isAnimating 
            ? 'scale-100 opacity-100 translate-y-0' 
            : 'scale-75 opacity-0 translate-y-8'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-purple-200/30">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 rounded-xl flex items-center justify-center">
              <Send className="w-4 h-4 text-white" />
            </div>
            <h2 className="text-lg font-bold text-gray-900">Send Feedback</h2>
          </div>
          <button
            onClick={handleClose}
            disabled={isSubmitting || isClosing}
            className="p-2 hover:bg-purple-100 rounded-xl transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-10 pb-10">
          {isSuccess ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Thank you!</h3>
              <p className="text-gray-600">Your feedback has been submitted successfully.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Star Rating */}
              <div className="mt-20">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Rate your experience (optional)
                </label>
                <div className="flex items-center justify-center space-x-1 py-4">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setRating(star)}
                      onMouseEnter={() => setHoveredRating(star)}
                      onMouseLeave={() => setHoveredRating(0)}
                      className="p-2 hover:scale-110 transition-transform duration-200"
                      disabled={isSubmitting || isClosing}
                    >
                      <Star
                        className={`w-8 h-8 transition-colors duration-200 ${
                          star <= (hoveredRating || rating)
                            ? 'text-yellow-400 fill-yellow-400'
                            : 'text-gray-300 hover:text-yellow-300'
                        }`}
                      />
                    </button>
                  ))}
                  {rating > 0 && (
                    <span className="ml-3 text-sm text-gray-600 font-medium">
                      {rating === 1 && 'Poor'}
                      {rating === 2 && 'Fair'}
                      {rating === 3 && 'Good'}
                      {rating === 4 && 'Great'}
                      {rating === 5 && 'Excellent'}
                    </span>
                  )}
                </div>
              </div>

              <div>
                <label htmlFor="feedback-comment" className="block text-sm font-medium text-gray-700 mb-2">
                  Your feedback
                </label>
                <textarea
                  id="feedback-comment"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Please share your thoughts, suggestions, or report any issues..."
                  className="w-full h-32 px-4 py-3 border border-purple-200/60 rounded-2xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100/50 outline-none transition-all duration-200 resize-none font-medium"
                  disabled={isSubmitting || isClosing}
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-3">
                  <p className="text-sm text-red-600 font-medium">{error}</p>
                </div>
              )}

              <div className="flex items-center justify-between pt-2">
                <p className="text-xs text-gray-500">
                  User type: <span className="font-medium text-purple-600">{accessLevel}</span>
                </p>
                
                <div className="flex space-x-3">
                  <button
                    type="button"
                    onClick={handleClose}
                    disabled={isSubmitting || isClosing}
                    className="px-4 py-2 border border-purple-200 text-gray-700 font-medium rounded-xl hover:bg-purple-50 transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  
                  <button
                    type="submit"
                    disabled={!comment.trim() || isSubmitting || isClosing}
                    className="px-6 py-2 bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 hover:from-purple-700 hover:via-purple-800 hover:to-violet-900 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-xl shadow-lg transition-all duration-200 hover:shadow-xl hover:scale-105 active:scale-95"
                  >
                    {isSubmitting ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        <span>Sending...</span>
                      </div>
                    ) : (
                      'Submit Feedback'
                    )}
                  </button>
                </div>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default FeedbackModal; 