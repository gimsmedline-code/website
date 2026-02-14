import { Link } from "react-router-dom";
import { CATEGORY_IMAGES } from "../lib/products";

const PRODUCT_CATEGORIES = [
  {
    name: "Cardiac Surgery",
    path: "/products/cardiac-surgery",
    description:
      "Precision instruments and devices for cardiac surgical procedures",
  },
  {
    name: "Critical Care",
    path: "/products/critical-care",
    description: "Essential equipment for intensive care units",
  },
  {
    name: "Cardiology",
    path: "/products/cardiology",
    description: "Diagnostic and therapeutic solutions for cardiac care",
  },
  {
    name: "Urology",
    path: "/products/urology",
    description: "Specialized devices for urological procedures",
  },
  {
    name: "Nephrology",
    path: "/products/nephrology",
    description: "Solutions for kidney and renal care management",
  },
  {
    name: "Interventional Radiology",
    path: "/products/interventional-radiology",
    description: "Imaging and intervention tools for radiological procedures",
  },
  {
    name: "Anesthesiology",
    path: "/products/anesthesiology",
    description: "Equipment for anesthesia delivery and monitoring",
  },
  {
    name: "Gastroenterology",
    path: "/products/gastroenterology",
    description: "Endoscopic and gastrointestinal care solutions",
  },
];

export default function Products() {
  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-primary/5 via-transparent to-accent/5">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold font-display text-primary mb-6">
            Our Product Portfolio
          </h1>
          <p className="text-lg text-muted-foreground mb-6">
            At GIMS MEDLINE, our product portfolio reflects a deliberate commitment to clinical precision, safety, and performance. We offer carefully curated medical solutions across multiple healthcare specialties, ensuring that every product we represent meets the practical demands of modern clinical environments. Our focus is not simply on supply, but on supporting clinical excellence through thoughtfully selected medical devices and disposables.
          </p>
          <p className="text-lg text-muted-foreground">
            We collaborate with both domestic manufacturers and internationally sourced brands to ensure access to advanced medical technologies and globally recognized quality benchmarks. Select products are imported and meet applicable international certifications, allowing healthcare providers to benefit from innovations aligned with evolving global standards.
          </p>
        </div>
      </section>

      {/* Product Categories Grid */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {PRODUCT_CATEGORIES.map((category) => (
              <Link
                key={category.path}
                to={category.path}
                className="group h-full bg-white border border-border rounded-lg hover:border-accent hover:shadow-lg transition-all duration-200 overflow-hidden flex flex-col"
              >
                <div className="h-48 overflow-hidden relative">
                  <img
                    src={CATEGORY_IMAGES[category.path.split("/").pop() || ""]}
                    alt={category.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-60" />
                </div>
                <div className="p-6 flex flex-col flex-grow">
                  <h3 className="text-lg font-semibold text-primary group-hover:text-accent transition-colors mb-3">
                    {category.name}
                  </h3>
                  <p className="text-sm text-muted-foreground flex-grow">
                    {category.description}
                  </p>
                  <div className="mt-4 text-accent group-hover:translate-x-1 transition-transform self-end">
                    →
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold font-display text-primary mb-6">
            Looking for a Specific Solution?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Contact our team to discuss your specific needs and find the right
            products for your organization
          </p>
          <Link
            to="/contact"
            className="inline-block px-8 py-3 bg-accent text-accent-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
          >
            Request a Consultation
          </Link>
        </div>
      </section>
    </div>
  );
}
