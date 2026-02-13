import { Link, useLocation } from "react-router-dom";

interface PlaceholderProps {
  title: string;
  description: string;
}

export function PlaceholderPage({ title, description }: PlaceholderProps) {
  const location = useLocation();

  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-primary/5 via-transparent to-accent/5">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold font-display text-primary mb-6">
            {title}
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl">
            {description}
          </p>
        </div>
      </section>

      {/* Content Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <div className="mb-8 p-12 bg-background rounded-lg border border-border">
              <h2 className="text-2xl font-semibold text-primary mb-4">
                Coming Soon
              </h2>
              <p className="text-muted-foreground mb-6">
                This page is currently being developed. We're working to bring
                you the best content for {title.toLowerCase()}.
              </p>
              <p className="text-sm text-muted-foreground mb-8">
                For more information about our services and products, feel free
                to browse our other pages or contact us directly.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/"
                className="px-8 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
              >
                Back to Home
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
      </section>
    </div>
  );
}
