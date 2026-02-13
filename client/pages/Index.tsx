import { Link } from "react-router-dom";

const SPECIALTIES = [
  { name: "Cardiac Surgery", path: "/products/cardiac-surgery" },
  { name: "Critical Care", path: "/products/critical-care" },
  { name: "Cardiology", path: "/products/cardiology" },
  { name: "Urology", path: "/products/urology" },
  { name: "Nephrology", path: "/products/nephrology" },
  {
    name: "Interventional Radiology",
    path: "/products/interventional-radiology",
  },
  { name: "Anesthesiology", path: "/products/anesthesiology" },
  { name: "Gastroenterology", path: "/products/gastroenterology" },
];

export default function Index() {
  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="relative py-20 md:py-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />
        <div className="absolute top-0 right-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />

        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold font-display text-primary mb-6 leading-tight">
              Advancing Clinical Outcomes Through Thoughtfully Selected Medical
              Products
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 leading-relaxed">
              At GIMS MEDLINE, we focus on one thing that truly matters in
              healthcare — clinical reliability. Every product we represent is
              chosen with a deep understanding of how it performs in real
              clinical settings, not just on paper.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                to="/products"
                className="px-8 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200 text-center inline-block"
              >
                Explore Products
              </Link>
              <Link
                to="/contact"
                className="px-8 py-3 border-2 border-primary text-primary font-semibold rounded-lg hover:bg-primary hover:text-primary-foreground transition-all duration-200 text-center inline-block"
              >
                Contact Us
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* About Intro Section */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold font-display text-primary mb-6">
            A Clinically Aligned Approach to Medical Products
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl">
            Healthcare today demands more than availability. It demands
            consistency, performance, and confidence.
          </p>

          <div className="bg-white p-8 rounded-lg border border-border">
            <h3 className="text-xl font-semibold text-primary mb-6">
              At GIMS MEDLINE, we evaluate products based on:
            </h3>
            <ul className="space-y-3">
              <li className="flex items-start gap-4">
                <span className="flex-shrink-0 w-2 h-2 rounded-full bg-accent mt-2" />
                <span className="text-foreground">Clinical usability</span>
              </li>
              <li className="flex items-start gap-4">
                <span className="flex-shrink-0 w-2 h-2 rounded-full bg-accent mt-2" />
                <span className="text-foreground">Performance consistency</span>
              </li>
              <li className="flex items-start gap-4">
                <span className="flex-shrink-0 w-2 h-2 rounded-full bg-accent mt-2" />
                <span className="text-foreground">
                  Compatibility with established procedures
                </span>
              </li>
              <li className="flex items-start gap-4">
                <span className="flex-shrink-0 w-2 h-2 rounded-full bg-accent mt-2" />
                <span className="text-foreground">
                  Acceptance among healthcare professionals
                </span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Areas We Serve Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold font-display text-primary mb-4">
            Focused Across Key Clinical Specialties
          </h2>
          <p className="text-lg text-muted-foreground mb-12 max-w-2xl">
            Our portfolio spans multiple healthcare specialties, each supported
            with carefully selected products
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {SPECIALTIES.map((specialty) => (
              <Link
                key={specialty.path}
                to={specialty.path}
                className="group p-6 bg-white border border-border rounded-lg hover:border-accent hover:shadow-lg transition-all duration-200"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-primary group-hover:text-accent transition-colors">
                    {specialty.name}
                  </h3>
                  <span className="text-2xl text-accent/30 group-hover:text-accent group-hover:translate-x-1 transition-all">
                    →
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  Clinical solutions for {specialty.name.toLowerCase()}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Relationship Section */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold font-display text-primary mb-8 max-w-2xl">
            Built on Professional Relationships
          </h2>

          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-lg text-foreground mb-6 leading-relaxed">
                Healthcare is built on collaboration. We work closely with
                clinicians, nursing teams, and hospital administration to ensure
                our offerings integrate smoothly into clinical workflows.
              </p>
              <p className="text-lg text-foreground leading-relaxed">
                Our focus is not transactional. It is relational — rooted in
                responsiveness, clarity, and long-term professional engagement.
              </p>
            </div>
            <div className="bg-gradient-to-br from-primary/10 to-accent/10 rounded-lg p-8 md:p-12">
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-accent font-semibold">→</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-primary mb-1">
                      Clinical Teams
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Direct engagement with treating physicians and specialists
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-accent font-semibold">→</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-primary mb-1">
                      Nursing Teams
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Support for daily operational implementation
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-accent font-semibold">→</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-primary mb-1">
                      Administration
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Partnership with procurement and hospital leadership
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Statement Banner */}
      <section className="py-16 md:py-20 bg-primary text-primary-foreground">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl">
            <p className="text-xl md:text-2xl font-semibold leading-relaxed">
              GIMS MEDLINE stands for thoughtful selection, professional
              integrity, and commitment to clinical excellence.
            </p>
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
            Explore our product portfolio or reach out to discuss how we can
            support your healthcare organization
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
