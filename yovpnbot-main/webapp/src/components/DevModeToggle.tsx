'use client';

import { useState } from 'react';
import { useStore } from '@/hooks/useStore';
import { cn } from '@/lib/utils';

export default function DevModeToggle() {
  const { devMode, setDevMode } = useStore();
  const [isOpen, setIsOpen] = useState(false);
  const [mockUserId, setMockUserId] = useState(devMode.mockUserId?.toString() || '');
  const [mockUri, setMockUri] = useState(devMode.mockSubscriptionUri || '');

  if (!devMode.enabled) return null;

  const handleSave = () => {
    setDevMode({
      enabled: true,
      mockUserId: mockUserId ? parseInt(mockUserId) : undefined,
      mockSubscriptionUri: mockUri || undefined,
    });
    setIsOpen(false);
  };

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'fixed bottom-4 right-4 z-50',
          'bg-yellow-500 text-black font-bold',
          'w-12 h-12 rounded-full shadow-lg',
          'flex items-center justify-center',
          'hover:bg-yellow-400 transition-colors',
          'border-2 border-yellow-600'
        )}
        title="Dev Mode Settings"
      >
        🛠️
      </button>

      {/* Settings Panel */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
          <div className="glass-dark rounded-2xl p-6 max-w-md w-full border border-yellow-500/50">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-yellow-400">🛠️ Dev Mode</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              {/* Mock User ID */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Mock User ID
                </label>
                <input
                  type="number"
                  value={mockUserId}
                  onChange={(e) => setMockUserId(e.target.value)}
                  placeholder="123456789"
                  className="w-full px-4 py-2 bg-black/50 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none"
                />
              </div>

              {/* Mock Subscription URI */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Mock Subscription URI
                </label>
                <textarea
                  value={mockUri}
                  onChange={(e) => setMockUri(e.target.value)}
                  placeholder="v2ray://..."
                  rows={4}
                  className="w-full px-4 py-2 bg-black/50 border border-gray-600 rounded-lg text-white focus:border-yellow-500 focus:outline-none resize-none"
                />
              </div>

              {/* Save Button */}
              <button
                onClick={handleSave}
                className="w-full bg-yellow-500 text-black font-bold py-3 rounded-lg hover:bg-yellow-400 transition-colors"
              >
                Save Settings
              </button>

              {/* Info */}
              <div className="text-xs text-gray-400 mt-4 p-3 bg-black/30 rounded-lg">
                <p className="mb-2">⚠️ Development Mode is enabled</p>
                <p>This panel allows you to test the app without Telegram integration.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
