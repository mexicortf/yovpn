import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text);
  } else {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      textArea.remove();
      return Promise.resolve();
    } catch (error) {
      textArea.remove();
      return Promise.reject(error);
    }
  }
}

export function openDeepLink(uri: string, platform: string) {
  const deepLinks: Record<string, string> = {
    android: `v2raytun://import/${encodeURIComponent(uri)}`,
    ios: `v2raytun://import/${encodeURIComponent(uri)}`,
    macos: `v2raytun://import/${encodeURIComponent(uri)}`,
    windows: `v2raytun://import/${encodeURIComponent(uri)}`,
    androidtv: `v2raytun://import/${encodeURIComponent(uri)}`,
  };

  const deepLink = deepLinks[platform] || uri;
  
  // Try to open deep link
  window.location.href = deepLink;
  
  // Fallback: copy to clipboard if deep link fails
  setTimeout(() => {
    copyToClipboard(uri);
  }, 1000);
}

export function detectUserPlatform(): string {
  const userAgent = navigator.userAgent.toLowerCase();
  
  if (/android/i.test(userAgent)) {
    return 'android';
  }
  if (/iphone|ipad|ipod/i.test(userAgent)) {
    return 'ios';
  }
  if (/mac os x/i.test(userAgent)) {
    return 'macos';
  }
  if (/windows/i.test(userAgent)) {
    return 'windows';
  }
  
  return 'android'; // Default
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
}

export function isExpired(dateString: string): boolean {
  return new Date(dateString) < new Date();
}
