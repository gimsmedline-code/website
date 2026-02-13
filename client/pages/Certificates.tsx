import { Link } from "react-router-dom";
import { PlaceholderPage } from "./Placeholder";

const CERTIFICATE_CATEGORIES = [
  {
    title: "Regulatory Certifications",
    description:
      "Compliance certifications from international regulatory bodies",
  },
  {
    title: "Import Certifications",
    description: "Official import and customs clearance documentation",
  },
  {
    title: "Compliance Approvals",
    description: "Quality and safety compliance certifications",
  },
  {
    title: "Manufacturer Quality Certificates",
    description: "Original quality certificates from manufacturers",
  },
];

export default function Certificates() {
  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-primary/5 via-transparent to-accent/5">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold font-display text-primary mb-6">
            Regulatory Certifications
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl">
            Comprehensive documentation ensuring compliance and quality
            standards
          </p>
        </div>
      </section>

      {/* Certificates Grid */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            {CERTIFICATE_CATEGORIES.map((category, index) => (
              <div
                key={index}
                className="p-8 bg-white border border-border rounded-lg hover:shadow-lg transition-all duration-200"
              >
                <h3 className="text-xl font-semibold text-primary mb-3">
                  {category.title}
                </h3>
                <p className="text-muted-foreground mb-6">
                  {category.description}
                </p>
                <button
                  disabled
                  className="px-6 py-2 bg-primary text-primary-foreground rounded font-medium text-sm opacity-50 cursor-not-allowed"
                >
                  View Certificates
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Coming Soon Notice */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold font-display text-primary mb-4">
              Document Repository Coming Soon
            </h2>
            <p className="text-muted-foreground mb-8">
              We are organizing our complete certification and compliance
              documentation. For immediate access to specific certificates,
              please contact our team.
            </p>
            <Link
              to="/contact"
              className="inline-block px-8 py-3 bg-accent text-accent-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
            >
              Request Certificates
            </Link>
          </div>
        </div>
      </section>

      {/* Compliance Statement */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto p-8 bg-gradient-to-br from-primary/5 to-accent/5 rounded-lg border border-border">
            <h3 className="text-xl font-semibold text-primary mb-4">
              Our Commitment to Quality
            </h3>
            <p className="text-foreground leading-relaxed">
              Every product in our portfolio meets rigorous quality standards.
              Our suppliers include manufacturers with European regulatory
              approvals and internationally recognized compliance
              certifications. We maintain complete documentation of all
              certifications and are available to provide detailed compliance
              information upon request.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
