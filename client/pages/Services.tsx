import { Link } from "react-router-dom";

const SERVICES = [
  {
    title: "Clinical Product Consultation",
    description:
      "Expert guidance on product selection and clinical integration based on your organization's needs",
  },
  {
    title: "Hospital Procurement Support",
    description:
      "End-to-end support for procurement processes including specification matching and vendor coordination",
  },
  {
    title: "Product Education & Training",
    description:
      "Comprehensive training programs for clinical and nursing staff on product usage and best practices",
  },
  {
    title: "After-Sales Support",
    description:
      "Ongoing technical support and coordination for product-related inquiries and maintenance",
  },
  {
    title: "Logistics & Supply Chain",
    description:
      "Reliable supply continuity assistance and logistics management for seamless inventory operations",
  },
  {
    title: "Professional Partnerships",
    description:
      "Long-term relational partnerships focused on clinical excellence and organizational success",
  },
];

export default function Services() {
  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-primary/5 via-transparent to-accent/5">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold font-display text-primary mb-6">
            Professional Services
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl">
            Comprehensive support to ensure successful implementation and
            ongoing partnership
          </p>
        </div>
      </section>

      {/* Services Grid */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8 mb-12">
            {SERVICES.map((service, index) => (
              <div
                key={index}
                className="p-6 bg-background rounded-lg border border-border hover:border-accent hover:shadow-lg transition-all duration-200"
              >
                <div className="flex items-start gap-4 mb-3">
                  <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-accent font-bold">→</span>
                  </div>
                  <h3 className="text-lg font-semibold text-primary">
                    {service.title}
                  </h3>
                </div>
                <p className="text-muted-foreground">{service.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Our Approach */}
      <section className="py-16 md:py-24 bg-primary text-primary-foreground">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold font-display mb-8">
            Our Service Philosophy
          </h2>
          <div className="grid md:grid-cols-2 gap-12">
            <div>
              <p className="text-lg leading-relaxed mb-6">
                At GIMS MEDLINE, we believe that exceptional products require
                exceptional service. Our team is committed to building lasting
                partnerships with our healthcare clients.
              </p>
              <p className="text-lg leading-relaxed">
                We don't simply supply products — we partner with your
                organization to ensure clinical success and operational
                excellence.
              </p>
            </div>
            <div>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <span className="text-accent text-xl">✓</span>
                  <span>Responsive to clinical needs</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent text-xl">✓</span>
                  <span>Dedicated account support</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent text-xl">✓</span>
                  <span>Proactive supply management</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-accent text-xl">✓</span>
                  <span>Long-term relationship focus</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold font-display text-primary mb-6">
            Ready to Partner With Us?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Let's discuss how our services can support your organization's
            clinical and operational goals
          </p>
          <Link
            to="/contact"
            className="inline-block px-8 py-3 bg-accent text-accent-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
          >
            Contact Us Today
          </Link>
        </div>
      </section>
    </div>
  );
}
