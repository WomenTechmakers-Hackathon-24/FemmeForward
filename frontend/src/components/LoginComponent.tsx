import { useAuth } from "@/AuthContext";
import { FaGoogle } from "react-icons/fa"; // Import the Google icon from React Icons

const LoginComponent: React.FC = () => {
  const { login, rememberMe, setRememberMe } = useAuth();
  
  return (
    <div className="flex flex-col space-y-4">
      <button 
        onClick={login}
        className="px-4 py-2 bg-indigo-500 text-white rounded flex items-center space-x-2 hover:bg-blue-600"
      >
        <FaGoogle className="w-5 h-5" /> {/* Google icon */}
        <span>Sign in with Google</span>
      </button>
      <label className="flex items-center space-x-2">
        <input
          type="checkbox"
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
          className="form-checkbox"
        />
        <span>Remember me</span>
      </label>
    </div>
  );
};

export default LoginComponent;
