import React, { useState } from 'react';
import { useAuth } from '../AuthContext';

const Registration: React.FC = () => {
  const { user, completeRegistration } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const formData = new FormData(e.currentTarget);
      const birthdate = formData.get('birthdate') as string;
      
      // Basic validation - ensure user is at least 13 years old
      const birthdateDate = new Date(birthdate);
      const today = new Date();
      const age = today.getFullYear() - birthdateDate.getFullYear();
      const monthDiff = today.getMonth() - birthdateDate.getMonth();
      
      if (age < 13 || (age === 13 && monthDiff < 0)) {
        throw new Error('You must be at least 13 years old to register.');
      }

      await completeRegistration({
        name: formData.get('name') as string,
        birthdate: birthdate,
      });
    } catch (error) {
      console.error('Registration error:', error);
      setError(error instanceof Error ? error.message : 'Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const maxDate = () => {
    const date = new Date();
    date.setFullYear(date.getFullYear() - 13);
    return date.toISOString().split('T')[0];
  };

  return (
    <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Complete Registration</h2>
      <p className="mb-4">Welcome {user?.email}! Please complete your registration.</p>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
            Name
          </label>
          <input
            type="text"
            id="name"
            name="name"
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div className="mb-4">
          <label htmlFor="birthdate" className="block text-sm font-medium text-gray-700">
            Birth Date
          </label>
          <input
            type="date"
            id="birthdate"
            name="birthdate"
            required
            max={maxDate()}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            You must be at least 13 years old to register.
          </p>
        </div>
        
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Registering...' : 'Complete Registration'}
        </button>
      </form>
    </div>
  );
};

export default Registration;