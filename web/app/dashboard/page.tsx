import { requireAuth } from '@/lib/auth';
import LogoutButton from '@/components/LogoutButton';

export default async function DashboardPage() {
  // Server-side authentication check
  const user = await requireAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Welcome, {user.email}
              </span>
              <LogoutButton />
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
            <div className="text-center">
              <div className="mx-auto h-12 w-12 text-primary-600 mb-4">
                <svg fill="none" stroke="currentColor" viewBox="0 0 48 48">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Authentication Successful!
              </h2>
              <p className="text-gray-600 mb-6">
                You have successfully logged in and can access this protected page.
              </p>

              {/* User information card */}
              <div className="bg-white rounded-lg shadow p-6 max-w-md mx-auto">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Your Account</h3>
                <dl className="space-y-3">
                  <div className="flex justify-between">
                    <dt className="text-sm font-medium text-gray-500">User ID</dt>
                    <dd className="text-sm text-gray-900">{user.id}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm font-medium text-gray-500">Email</dt>
                    <dd className="text-sm text-gray-900">{user.email}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm font-medium text-gray-500">Member since</dt>
                    <dd className="text-sm text-gray-900">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                    </dd>
                  </div>
                </dl>
              </div>

              {/* Feature highlights */}
              <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-green-600 mb-2">
                    <svg className="h-6 w-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h4 className="text-sm font-medium text-gray-900">Secure Authentication</h4>
                  <p className="text-xs text-gray-500 mt-1">JWT tokens with httpOnly cookies</p>
                </div>

                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-blue-600 mb-2">
                    <svg className="h-6 w-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <h4 className="text-sm font-medium text-gray-900">CSRF Protection</h4>
                  <p className="text-xs text-gray-500 mt-1">Custom headers and SameSite cookies</p>
                </div>

                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-purple-600 mb-2">
                    <svg className="h-6 w-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h4 className="text-sm font-medium text-gray-900">Rate Limited</h4>
                  <p className="text-xs text-gray-500 mt-1">Protection against brute force attacks</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}