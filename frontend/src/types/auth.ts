export interface UserData {
    id: string;
    email: string;
    birthdate: string; // Format: YYYY-MM-DD
    name: string;
    interests: string[];
  }
  
  export interface LoadingState {
    auth: boolean;
    registration: boolean;
    profileCheck: boolean;
  }
  