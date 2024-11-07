const LoadingSpinner = () => {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="relative">
        {/* Spinner */}
        <div className="w-12 h-12 rounded-full border-4 border-blue-200 animate-spin">
          <div className="absolute top-0 left-0 w-12 h-12 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"></div>
        </div>
        {/* Loading text */}
        <div className="mt-4 text-center text-gray-600">Loading...</div>
      </div>
    </div>
  );
};

export default LoadingSpinner;