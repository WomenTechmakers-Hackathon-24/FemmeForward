import { useAuth } from "@/AuthContext";

interface TaskBarComponentProps {
  onBack: () => void;
  onProfileClick: () => void;
};

const TaskbarComponent: React.FC<TaskBarComponentProps> = ({ onBack, onProfileClick }) => {
  const { userData, logout } = useAuth();
  
  if (!userData) {
    return <></>;
  }

  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty) {
      case "beginner":
        return "bg-green-500"; // Green for beginner
      case "intermediate":
        return "bg-yellow-500"; // Yellow for intermediate
      case "advanced":
        return "bg-red-500"; // Red for hard
      default:
        return "bg-gray-500"; // Default gray if difficulty is unknown
    }
  };

  return (
    <div>
      <div className="taskbar bg-purple-700 text-white p-4 flex justify-between items-center w-full fixed top-0 left-0">
        <div className="flex items-center space-x-2" onClick={() => onBack()}>
          <img className="logo-taskbar w-6 h-6" src="FemmeForward.ico" alt="Logo" />
          <div className="text-lg font-bold">Femme Forward</div>
        </div> {/* Logo and title on the left */}
        
        <div className="flex items-center space-x-4"> {/* Added space between elements */}
          <h1 className="text-lg" onClick={() => onProfileClick()}>
            Welcome, {userData.name}!
          </h1>

          {/* Circular difficulty icon */}
          <div 
            className={`w-6 h-6 rounded-full ${getDifficultyColor(userData?.difficulty_level)} flex items-center justify-center text-white`}>
            {/* You can add an icon or just leave it as a colored circle */}
          </div>
          
          <button className="bg-purple-200 hover:bg-red-600 text-black p-2 rounded" onClick={logout}>
            Log out
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskbarComponent;
