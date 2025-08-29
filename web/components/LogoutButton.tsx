'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ClientAuth } from '@/lib/auth';

export default function LogoutButton() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleLogout = async () => {
    setIsLoading(true);

    try {
      await ClientAuth.logout();
      // Always redirect to login, regardless of logout API result
      // This ensures the user is signed out even if the API call fails
      router.push('/login');
      router.refresh(); // Refresh to clear any cached auth state
    } catch (error) {
      // Even if logout fails, redirect to login page
      router.push('/login');
      router.refresh();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleLogout}
      disabled={isLoading}
      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {isLoading ? (
        <>
          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-2"></div>
          Signing out...
        </>
      ) : (
        'Sign out'
      )}
    </button>
  );
}