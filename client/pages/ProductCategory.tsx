import { useParams, Link } from "react-router-dom";
import { PRODUCTS } from "../lib/products";

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

          {/* Products Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {PRODUCTS.filter((p) => p.category === category).map((product) => (
              <div
                key={product.id}
                className="group bg-white border border-border rounded-lg overflow-hidden hover:shadow-lg transition-all duration-200"
              >
                <div className="h-64 overflow-hidden relative">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-semibold text-primary mb-3">
                    {product.name}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
                    {product.description}
                  </p>
                  <div className="flex gap-3">
                    <Link
                      to="/contact"
                      className="flex-1 px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded hover:bg-opacity-90 transition-all text-center"
                    >
                      Enquire
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {PRODUCTS.filter((p) => p.category === category).length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No products listed in this category yet. Please contact us for the full catalog.</p>
            </div>
          )}
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
