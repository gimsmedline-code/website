import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname,
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background py-20 px-4">
      <div className="text-center max-w-2xl">
        <h1 className="text-6xl md:text-7xl font-bold font-display text-primary mb-4">
          404
        </h1>
        <h2 className="text-2xl md:text-3xl font-bold text-primary mb-4">
          Page Not Found
        </h2>
        <p className="text-lg text-muted-foreground mb-8">
          The page you're looking for doesn't exist. It may have been moved or
          is no longer available.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/"
            className="px-8 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
          >
            Return to Home
          </Link>
          <Link
            to="/contact"
            className="px-8 py-3 border-2 border-primary text-primary font-semibold rounded-lg hover:bg-primary hover:text-primary-foreground transition-all duration-200"
          >
            Contact Us
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
