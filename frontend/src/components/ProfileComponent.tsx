import { useAuth } from '@/AuthContext';
import React from 'react';

const ProfileComponent: React.FC = () => {
    const { userData } = useAuth();
  return (
    <div>
      <h2 className="text-2xl font-semibold">User Profile</h2>
      {/* Profile details go here */}
      <h3>Hello {userData?.name}</h3>
      <h3>Email: {userData?.email}</h3>
      <h3>Birthdate: {userData?.birthdate}</h3>
    </div>
  );
};

export default ProfileComponent;
