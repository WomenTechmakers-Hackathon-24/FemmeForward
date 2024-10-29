import { useAuth } from "@/AuthContext";

const LoginComponent: React.FC = () => {
    const { login, rememberMe, setRememberMe } = useAuth();
  
    return (
      <div className="flex flex-col space-y-4">
        <button 
          onClick={login}
          className="px-4 py-2 bg-indigo-500 text-white rounded hover:bg-blue-600"
        >
          Sign in with Google
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