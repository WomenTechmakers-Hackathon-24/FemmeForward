import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { UserCircle, Calendar } from "lucide-react";

const Registration = () => {
  const { user, completeRegistration, logout } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

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
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold tracking-tight">Complete Registration</CardTitle>
          <CardDescription className="text-gray-500">
            Welcome back, {user?.email}! Please complete your profile. 
            <button 
              onClick={logout} 
              className="text-sm text-blue-600 underline hover:text-blue-800 italic ml-2" // Added margin-left
            >
              Not you?
            </button>
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-sm font-medium">
                Full Name
              </Label>
              <div className="relative">
                <UserCircle className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                <Input
                  id="name"
                  name="name"
                  required
                  className="pl-10"
                  placeholder="Enter your full name"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="birthdate" className="text-sm font-medium">
                Birth Date
              </Label>
              <div className="relative">
                <Calendar className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                <Input
                  type="date"
                  id="birthdate"
                  name="birthdate"
                  required
                  max={maxDate()}
                  className="pl-10"
                />
              </div>
              <p className="text-sm text-gray-500">
                You must be at least 13 years old to register.
              </p>
            </div>

            <Button
              type="submit"
              disabled={isSubmitting}
              className="w-full"
            >
              {isSubmitting ? 'Creating your account...' : 'Complete Registration'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Registration;