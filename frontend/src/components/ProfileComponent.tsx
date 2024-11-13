import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import InterestsComponent from './Topic/InterestsComponent'; // Import the InterestsSelection component
import api from '@/api/axios';
import { UserData } from '@/types/auth';

const Profile = () => {
  const [tags, setTags] = useState<string[]>([]);
  const [userInterests, setUserInterests] = useState<string[]>([]);
  const [isEditable, setIsEditable] = useState(false);  // Determine if fields can be edited
  const [userProfile, setUserProfile] = useState<UserData>();
  const [originalProfile, setOriginalProfile] = useState<UserData | undefined>(); // Store original data for canceling edits
  const [message, setMessage] = useState<string | null>(null); // State for success/error messages

  useEffect(() => {
    const computeAverage = (input: number[]) => {
      if (input.length === 0) return 0; // Handle case for empty array
      const sum = input.reduce((acc, num) => acc + num, 0);
      return sum / input.length;
    };

    const fetchProfileAndTags = async () => {
      try {
        const profileResponse = api.get(`/profile`);
        const tagsResponse = api.get(`/interests`);

        // Wait for both promises to resolve
        const [profileData, tagsData] = await Promise.all([profileResponse, tagsResponse]);
        const average = computeAverage(profileData.data.quiz_scores);
        const user = profileData.data;
        user.ave_score = average;
        setUserProfile(user); // Set profile data
        setOriginalProfile(user); // Save a copy of the original data
        setTags(tagsData.data); // Set tags data
      } catch (error) {
        console.error('Failed to load profile or tags:', error);
      }
    };

    fetchProfileAndTags();
  }, []);

  useEffect(() => {
    if (userProfile && tags.length > 0) {
      setUserInterests(userProfile?.interests || []); // Use the user profile data to set interests
    }
  }, [userProfile, tags]); // Trigger when userProfile or tags are updated

  const handleTagSelection = (tag: string) => {
    if (userInterests.includes(tag)) {
      setUserInterests(userInterests.filter(t => t !== tag));
    } else if (userInterests.length < 3) {
      setUserInterests([...userInterests, tag]);
    }
  };

  const isValidBirthdate = (birthdate: string) => {
    const birthDateObj = new Date(birthdate);
    const currentDate = new Date();
    const age = currentDate.getFullYear() - birthDateObj.getFullYear();
    const monthDiff = currentDate.getMonth() - birthDateObj.getMonth();
    const dayDiff = currentDate.getDate() - birthDateObj.getDate();

    // Check if age is less than 13 or if the month/day offsets adjust age under 13
    if (age < 13 || (age === 13 && (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)))) {
      return false;
    }
    return true;
  };

  const handleSaveChanges = async () => {
    if (!userProfile?.name || userProfile.name.length === 0)
    {
      setMessage('Failed: Name cannot be empty');
      return;
    }
    if (userProfile?.birthdate && !isValidBirthdate(userProfile.birthdate)) {
      setMessage('Failed: User must be at least 13 years old.');
      return; // Prevent saving if birthdate is less than 13 years old
    }

    if (userInterests.length === 0) {
      setMessage('Failed: You must select at least one interest before saving.');
      return; // Prevent saving if no interests are selected
    }

    try {
      const response = await api.put(`/profile`, {
        name: userProfile?.name,
        birthdate: userProfile?.birthdate,
        interests: userInterests,
      });
      setMessage('Profile saved successfully!');
      setIsEditable(false); // Proceed with saving and exiting edit mode
      setOriginalProfile(userProfile); // Update the original profile to match the new saved state
    } catch (error) {
      console.error('Failed to save profile:', error);
      setMessage('Failed to save profile. Please try again.');
    }
  };

  const cancelEditMode = () => {
    setUserProfile(originalProfile); // Revert to original profile data
    setIsEditable(false); // Exit edit mode
    setMessage(null); // Clear any messages
  };

  const handleInputChange = (field: string, value: string) => {
    setUserProfile((prevProfile) => ({
      ...prevProfile,
      [field]: value,
    }));
  };

  return (
    <div className="min-h-screen bg-violet-200 flex items-center justify-center pt-24">  
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          {message && (
              <div className={`p-2 rounded mb-4 ${message.includes('Failed') ? 'bg-red-200 text-red-800' : 'bg-green-200 text-green-800'}`}>
                {message}
              </div>
            )}
          <CardTitle className="text-2xl font-bold tracking-tight">Profile</CardTitle>
          <CardDescription className="text-gray-500">
            {isEditable ? (
              <input
                type="text"
                value={userProfile?.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="border p-2 rounded w-full"
              />
            ) : (
              <span>{userProfile?.name}</span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-bold">Birthdate</h3>
              {isEditable ? (
                <input
                  type="date"
                  value={userProfile?.birthdate}
                  onChange={(e) => handleInputChange('birthdate', e.target.value)}
                  className="border p-2 rounded w-full"
                />
              ) : (
                <p>{userProfile?.birthdate ? userProfile?.birthdate : 'N/A'}</p>
              )}
            </div>
            <div>
              <h3 className="text-lg font-bold">Age Group</h3>
              <p>{userProfile?.age_group ? userProfile?.age_group : 'N/A'}</p>
            </div>
            <div>
              <h3 className="text-lg font-bold">Difficulty</h3>
              <p>{userProfile?.difficulty_level ? userProfile?.difficulty_level : 'N/A'}</p>
            </div>
            <div>
              <h3 className="text-lg font-bold">Average Score</h3>
              <p>{userProfile?.ave_score ? userProfile?.ave_score : '0'}</p>
            </div>
            <h3 className="text-lg font-bold">Your Interests</h3>
            <InterestsComponent
              tags={tags}
              selectedInterests={userInterests}
              onTagSelection={handleTagSelection}
              isEditable={isEditable}
            />
          </div>
          {isEditable && (
            <div className="flex justify-between mt-4">
              <button onClick={handleSaveChanges} className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600">
                Save
              </button>
              <button onClick={cancelEditMode} className="bg-gray-300 py-2 px-4 rounded hover:bg-gray-400">
                Cancel
              </button>
            </div>
          )}
          {!isEditable && (
              <button
                onClick={() => setIsEditable(true)} // Toggle edit mode
                className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 my-5"
              >
                Edit Profile
              </button>
            )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Profile;
