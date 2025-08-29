'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ClientAuth, validatePassword } from '@/lib/auth';

const registerSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters long')
    .refine((password) => {
      const validation = validatePassword(password);
      return validation.isValid;
    }, 'Password must contain uppercase, lowercase, and digit'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState('');
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const password = watch('password');
  const passwordValidation = password ? validatePassword(password) : null;

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true);
    setApiError('');

    try {
      const result = await ClientAuth.register(data.email, data.password);

      if (result.success) {
        setSuccess(true);
        // Redirect to login after successful registration
        setTimeout(() => {
          router.push('/login');
        }, 2000);
      } else {
        setApiError(result.error || 'Registration failed');
      }
    } catch (error) {
      setApiError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 text-green-600">
              <svg fill="none" stroke="currentColor" viewBox="0 0 48 48">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="mt-4 text-center text-3xl font-extrabold text-gray-900">
              Registration Successful!
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              Redirecting you to login...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link
              href="/login"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              sign in to your existing account
            </Link>
          </p>
        </div>

        <div className="card">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            {apiError && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-700">{apiError}</div>
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  className="form-input"
                  placeholder="Enter your email"
                  {...register('email')}
                />
                {errors.email && (
                  <p className="error-message">{errors.email.message}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  type="password"
                  autoComplete="new-password"
                  className="form-input"
                  placeholder="Create a password"
                  {...register('password')}
                />
                {errors.password && (
                  <p className="error-message">{errors.password.message}</p>
                )}
                
                {/* Password strength indicator */}
                {password && passwordValidation && (
                  <div className="mt-2">
                    <div className="text-xs text-gray-600">Password requirements:</div>
                    <ul className="text-xs mt-1 space-y-1">
                      <li className={`flex items-center ${password.length >= 8 ? 'text-green-600' : 'text-gray-400'}`}>
                        <span className={`mr-2 ${password.length >= 8 ? 'text-green-600' : 'text-gray-400'}`}>
                          {password.length >= 8 ? '✓' : '○'}
                        </span>
                        At least 8 characters
                      </li>
                      <li className={`flex items-center ${/[A-Z]/.test(password) ? 'text-green-600' : 'text-gray-400'}`}>
                        <span className={`mr-2 ${/[A-Z]/.test(password) ? 'text-green-600' : 'text-gray-400'}`}>
                          {/[A-Z]/.test(password) ? '✓' : '○'}
                        </span>
                        One uppercase letter
                      </li>
                      <li className={`flex items-center ${/[a-z]/.test(password) ? 'text-green-600' : 'text-gray-400'}`}>
                        <span className={`mr-2 ${/[a-z]/.test(password) ? 'text-green-600' : 'text-gray-400'}`}>
                          {/[a-z]/.test(password) ? '✓' : '○'}
                        </span>
                        One lowercase letter
                      </li>
                      <li className={`flex items-center ${/\d/.test(password) ? 'text-green-600' : 'text-gray-400'}`}>
                        <span className={`mr-2 ${/\d/.test(password) ? 'text-green-600' : 'text-gray-400'}`}>
                          {/\d/.test(password) ? '✓' : '○'}
                        </span>
                        One number
                      </li>
                    </ul>
                  </div>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirm password
              </label>
              <div className="mt-1">
                <input
                  id="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  className="form-input"
                  placeholder="Confirm your password"
                  {...register('confirmPassword')}
                />
                {errors.confirmPassword && (
                  <p className="error-message">{errors.confirmPassword.message}</p>
                )}
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creating account...
                  </div>
                ) : (
                  'Create account'
                )}
              </button>
            </div>
          </form>
        </div>

        <div className="text-center">
          <Link
            href="/"
            className="text-sm text-primary-600 hover:text-primary-500"
          >
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}