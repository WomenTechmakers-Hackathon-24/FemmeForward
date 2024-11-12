export interface UserData {
    id?: string;
    email?: string;
    birthdate?: string; // Format: YYYY-MM-DD
    age_group?: string;
    difficulty_level?: string;
    quiz_scores?: number[];
    name?: string;
    interests?: string[];
    ave_score?: number;
  }
  
  export interface LoadingState {
    auth: boolean;
    registration: boolean;
    profileCheck: boolean;
  }
  