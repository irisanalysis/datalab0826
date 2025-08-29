import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">
            Auth System
          </h1>
          <p className="text-gray-600 mb-8">
            Secure authentication system with JWT tokens
          </p>
          
          <div className="space-y-4">
            <Link
              href="/login"
              className="block w-full py-3 px-4 bg-primary-600 text-white text-center rounded-md hover:bg-primary-700 transition duration-200"
            >
              Sign In
            </Link>
            
            <Link
              href="/register"
              className="block w-full py-3 px-4 border border-gray-300 text-gray-700 text-center rounded-md hover:bg-gray-50 transition duration-200"
            >
              Create Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}