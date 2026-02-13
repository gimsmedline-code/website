import { useParams, Link } from "react-router-dom";

const CATEGORIES = {
  "cardiac-surgery": {
    name: "Cardiac Surgery Solutions",
    description:
      "Products selected to support procedural precision and clinical reliability within cardiac surgical environments.",
  },
  "critical-care": {
    name: "Critical Care Solutions",
    description:
      "Essential equipment and devices for intensive care unit operations with proven clinical reliability.",
  },
  cardiology: {
    name: "Cardiology Solutions",
    description:
      "Diagnostic and therapeutic products for comprehensive cardiac care management.",
  },
  urology: {
    name: "Urology Solutions",
    description:
      "Specialized instruments and devices for urological procedures.",
  },
  nephrology: {
    name: "Nephrology Solutions",
    description:
      "Solutions for kidney disease management and renal care procedures.",
  },
  "interventional-radiology": {
    name: "Interventional Radiology Solutions",
    description:
      "Advanced imaging and intervention tools for minimally invasive radiological procedures.",
  },
  anesthesiology: {
    name: "Anesthesiology Solutions",
    description:
      "Equipment and devices for anesthesia delivery and patient monitoring.",
  },
  gastroenterology: {
    name: "Gastroenterology Solutions",
    description: "Endoscopic instruments and gastrointestinal care solutions.",
  },
};

export default function ProductCategory() {
  const { category } = useParams();
  const categoryData = category
    ? CATEGORIES[category as keyof typeof CATEGORIES]
    : null;

  if (!categoryData) {
    return (
      <div className="w-full">
        <section className="py-16 md:py-24 bg-gradient-to-br from-primary/5 via-transparent to-accent/5">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-4xl md:text-5xl font-bold font-display text-primary mb-6">
              Category Not Found
            </h1>
            <Link
              to="/products"
              className="inline-block px-8 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
            >
              Back to Products
            </Link>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-primary/5 via-transparent to-accent/5">
        <div className="container mx-auto px-4">
          <Link
            to="/products"
            className="inline-block mb-6 text-accent hover:text-accent/80 transition-colors font-medium text-sm"
          >
            ← Back to Products
          </Link>
          <h1 className="text-4xl md:text-5xl font-bold font-display text-primary mb-6">
            {categoryData.name}
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl">
            {categoryData.description}
          </p>
        </div>
      </section>

      {/* Products Listing Area */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl md:text-3xl font-bold font-display text-primary mb-12">
            Available Products
          </h2>

          <div className="bg-background p-12 rounded-lg border border-border text-center mb-12">
            <h3 className="text-xl font-semibold text-primary mb-4">
              Products Coming Soon
            </h3>
            <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
              We are currently curating the finest products for{" "}
              {categoryData.name.toLowerCase()}. Our team is working to ensure
              each product meets our rigorous clinical and quality standards.
            </p>
          </div>

          {/* Placeholder for future product listings */}
          <div className="grid md:grid-cols-3 gap-6 opacity-50">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="p-6 bg-white border border-border rounded-lg"
              >
                <h3 className="text-lg font-semibold text-primary mb-3">
                  Product Name
                </h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Product description will appear here
                </p>
                <div className="flex gap-2">
                  <button
                    disabled
                    className="flex-1 px-4 py-2 bg-primary text-primary-foreground text-sm rounded opacity-50 cursor-not-allowed"
                  >
                    Brochure
                  </button>
                  <button
                    disabled
                    className="flex-1 px-4 py-2 border border-primary text-primary text-sm rounded opacity-50 cursor-not-allowed"
                  >
                    Enquire
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-24 bg-primary text-primary-foreground">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold font-display mb-6">
            Interested in Our {categoryData.name}?
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto">
            Contact our team to discuss product availability and specifications
          </p>
          <Link
            to="/contact"
            className="inline-block px-8 py-3 bg-accent text-accent-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
          >
            Get in Touch
          </Link>
        </div>
      </section>
    </div>
  );
}
