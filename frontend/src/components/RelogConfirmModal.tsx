import React from 'react'
import { LogOut, AlertTriangle, X } from 'lucide-react'

interface RelogConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

const RelogConfirmModal: React.FC<RelogConfirmModalProps> = ({ isOpen, onClose, onConfirm }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white/95 backdrop-blur-md rounded-3xl border border-purple-200/50 shadow-2xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-purple-200/30">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">Confirm Logout</h2>
              <p className="text-sm text-gray-600">This action will clear all data</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-purple-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div className="flex items-start space-x-3">
            <LogOut className="w-5 h-5 text-gray-500 mt-0.5 flex-shrink-0" />
            <div className="space-y-2">
              <p className="text-gray-700 font-medium">
                You are about to log out of Afai by Aquaforest.
              </p>
              <p className="text-sm text-gray-600 leading-relaxed">
                This will clear all stored data including:
              </p>
              <ul className="text-sm text-gray-600 space-y-1 ml-4">
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-purple-400 rounded-full"></div>
                  <span>Your current authentication session</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-purple-400 rounded-full"></div>
                  <span>All conversation history</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-purple-400 rounded-full"></div>
                  <span>Session preferences and cache</span>
                </li>
              </ul>
              <p className="text-sm text-gray-600 bg-amber-50/80 rounded-lg p-3 border border-amber-200/50 mt-3">
                <span className="font-medium text-amber-700">Note:</span> You will need to enter your access code again to continue using the assistant.
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-purple-200/30">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-xl transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-6 py-2 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-xl hover:from-red-700 hover:to-red-800 transition-all duration-200 font-medium shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95"
          >
            Logout & Clear Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default RelogConfirmModal;