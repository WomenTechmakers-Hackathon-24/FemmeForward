import { useAuth } from "@/AuthContext";

interface TaskBarComponentProps {
  onBack: () => void;
  onProfileClick: () => void;
};
const TaskbarComponent: React.FC<TaskBarComponentProps> = ({onBack, onProfileClick}) => {
  const { userData, logout } = useAuth();
  
  if (!userData) {
    return <></>;
  }

  return (
    
    <div>
      <div className="taskbar bg-purple-700 text-white p-4 flex justify-between items-center w-full fixed top-0 left-0">
      <div className="text-lg font-bold" onClick={() => onBack()}>Empowering Women</div> {/* Logo or app name on the left */}
      <div className="flex items-center space-x-4"> {/* Added space between elements */}
        <h1 className="text-lg" onClick={() => onProfileClick()}>Welcome, {userData.name}!</h1>
        <button className="bg-purple-200 hover:bg-red-600 text-black p-2 rounded" onClick={logout}>Log out</button>
      </div>
      </div>
    </div>
  )
} 
export default TaskbarComponent;