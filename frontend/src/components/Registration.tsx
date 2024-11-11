import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { UserCircle, Calendar, ChevronLeft } from "lucide-react";
import api from '@/api/axios';

const Registration = () => {
  const { googleUser, completeRegistration, logout } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1); // Track which step of the registration
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [tags, setTags] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
  
    try {
      const formData = new FormData(e.currentTarget);
      const birthdate = formData.get('birthdate') as string;
      const birthdateDate = new Date(birthdate);
      const today = new Date();
      const age = today.getFullYear() - birthdateDate.getFullYear();
      const monthDiff = today.getMonth() - birthdateDate.getMonth();
  
      if (age < 13 || (age === 13 && monthDiff < 0)) {
        throw new Error('You must be at least 13 years old to register.');
      }
  
        try {
          const response = await api.get(`/interests`);
          setTags(response.data);
        }
        catch (error) {
          return;
        }
        setStep(2); // Move to the tag selection step
    } catch (error) {
      console.error('Registration error:', error);
      setError(error instanceof Error ? error.message : 'Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleCompleteRegistration = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // Prevent default form submission
    
    const formData = {
      //name: (document.querySelector('#name') as HTMLInputElement).value,
      //birthdate: (document.querySelector('#birthdate') as HTMLInputElement).value,
      //tags: selectedTags,
    };
  
    try {
      await completeRegistration(formData); // Send the data to the API
      // Handle successful registration (e.g., navigate to the homepage)
    } catch (error) {
      console.error('Registration failed:', error);
      setError('Failed to complete registration. Please try again.');
    }
  };

  const handleTagSelection = (tag: string) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else if (selectedTags.length < 3) {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  const maxDate = () => {
    const date = new Date();
    date.setFullYear(date.getFullYear() - 13);
    return date.toISOString().split('T')[0];
  };

  return (
    <div className="min-h-screen bg-violet-200 flex items-center justify-center p-4">
      {step === 1 ? (
        <Card className="w-full max-w-md">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold tracking-tight">Complete Registration</CardTitle>
            <CardDescription className="text-gray-500">
              Welcome back, {googleUser?.email}! Please complete your profile.
              <button
                onClick={logout}
                className="text-sm text-blue-600 underline hover:text-blue-800 italic ml-2"
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
                <Label htmlFor="name" className="text-sm font-medium">Full Name</Label>
                <div className="relative">
                  <UserCircle className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                  <Input id="name" name="name" required className="pl-10" placeholder="Enter your full name" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="birthdate" className="text-sm font-medium">Birth Date</Label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                  <Input type="date" id="birthdate" name="birthdate" required max={maxDate()} className="pl-10" />
                </div>
                <p className="text-sm text-gray-500">You must be at least 13 years old to register.</p>
              </div>
              <Button type="submit" disabled={isSubmitting} className="w-full bg-indigo-500">
                {isSubmitting ? 'Creating your account...' : 'Next'}
              </Button>
            </form>
          </CardContent>
        </Card>
      ) : (
        <Card className="w-full max-w-md">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold tracking-tight">Select Your Interests</CardTitle>
            <CardDescription className="text-gray-500">
              Choose up to 3 topics you are interested in.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-2">
              {tags.map(tag => (
                <Button
                  key={tag}
                  variant={selectedTags.includes(tag) ? 'default' : 'outline'}
                  onClick={() => handleTagSelection(tag)}
                >
                  {tag}
                </Button>
              ))}
            </div>
            <div className="flex items-center gap-4 mt-4">
              <Button
                variant="link" // Make it look like a link or a small button
                onClick={() => setStep(1)} // Go back to step 1
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center w-auto"
              >
                <ChevronLeft className="mr-2 h-4 w-4" /> Back
              </Button>
            </div>
            <form onSubmit={handleCompleteRegistration}> {/* Handle submit here */}
            <Button
              type="submit" // Now it is a submit button
              disabled={selectedTags.length === 0 || isSubmitting}
              className="w-full bg-indigo-500 mt-4"
            >
              {isSubmitting ? 'Completing registration...' : 'Complete Registration'}
            </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Registration;
