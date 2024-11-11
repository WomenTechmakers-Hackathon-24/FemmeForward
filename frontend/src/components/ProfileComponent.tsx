import api from '@/api/axios';
import { useAuth } from '@/AuthContext';
import React, { useEffect } from 'react';

const ProfileComponent: React.FC = () => {
    const { userData } = useAuth();

    const GetProfile = async () => {
      //setLoading(true);
      try {
        const response = await api.get(`/profile`);
        console.log(response);
        //setApiData(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        //setLoading(false);
      }
    }
    useEffect(() => {
      GetProfile();
    }, []); // Empty dependency array ensures it only runs once
    
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
