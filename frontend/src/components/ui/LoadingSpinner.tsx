interface LoadingSpinnerProps {
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message = "Loading..." }) => {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="flex items-center space-x-2">
        {/* Spinner */}
        <div className="w-8 h-8 rounded-full border-4 border-blue-200 animate-spin">
          <div className="absolute top-0 left-0 w-8 h-8 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"></div>
        </div>
        {/* Loading text */}
        <div className="text-center text-gray-600">{message}</div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
