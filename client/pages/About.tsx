import { Link } from "react-router-dom";

export default function About() {
  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-primary/5 via-transparent to-accent/5">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold font-display text-primary mb-6">
            About GIMS MEDLINE
          </h1>
        </div>
      </section>

      {/* Intro Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl">
            <p className="text-xl text-foreground mb-8 leading-relaxed">
              GIMS MEDLINE is a healthcare solutions organization committed to
              supporting modern clinical practice through a carefully curated
              portfolio of medical disposables and devices.
            </p>
            <p className="text-lg text-muted-foreground leading-relaxed">
              We understand that healthcare professionals demand more than
              product availability. They require consistency, reliability, and
              solutions that integrate seamlessly into existing clinical
              workflows.
            </p>
          </div>
        </div>
      </section>

      {/* Our Approach Section */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold font-display text-primary mb-12">
            Clinical Relevance Precedes Commercial Consideration
          </h2>

          <div className="grid md:grid-cols-2 gap-12">
            <div>
              <h3 className="text-xl font-semibold text-primary mb-6">
                Our Approach
              </h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-4">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
                    <span className="text-accent font-bold text-sm">✓</span>
                  </span>
                  <div>
                    <h4 className="font-semibold text-foreground mb-1">
                      Procedural Performance
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Reliability and precision in clinical settings
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-4">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
                    <span className="text-accent font-bold text-sm">✓</span>
                  </span>
                  <div>
                    <h4 className="font-semibold text-foreground mb-1">
                      Consistency
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Quality standards that don't vary
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-4">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
                    <span className="text-accent font-bold text-sm">✓</span>
                  </span>
                  <div>
                    <h4 className="font-semibold text-foreground mb-1">
                      Integration
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Ease of incorporation into clinical workflows
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-4">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
                    <span className="text-accent font-bold text-sm">✓</span>
                  </span>
                  <div>
                    <h4 className="font-semibold text-foreground mb-1">
                      Professional Acceptance
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Trust from healthcare professionals
                    </p>
                  </div>
                </li>
              </ul>
            </div>

            <div className="bg-gradient-to-br from-primary/10 to-accent/10 p-8 rounded-lg">
              <h3 className="text-xl font-semibold text-primary mb-6">
                Product Standards
              </h3>
              <p className="text-foreground mb-6 leading-relaxed">
                Our portfolio includes both domestically sourced and imported
                medical products selected to meet evolving healthcare
                requirements.
              </p>
              <p className="text-foreground mb-6 leading-relaxed">
                Several products we deal with are manufactured in facilities
                holding European regulatory approvals, reflecting
                internationally recognized compliance standards.
              </p>
              <div className="pt-6 border-t border-border">
                <p className="text-sm text-muted-foreground">
                  Every selection is driven by clinical evidence and healthcare
                  provider feedback, not marketing considerations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Professional Relationships Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold font-display text-primary mb-12">
            Our Professional Ecosystem
          </h2>

          <div className="grid md:grid-cols-4 gap-6">
            <div className="p-6 bg-background rounded-lg border border-border">
              <h3 className="text-lg font-semibold text-primary mb-3">
                Treating Doctors
              </h3>
              <p className="text-sm text-muted-foreground">
                Direct collaboration with clinical specialists to understand
                procedural requirements
              </p>
            </div>
            <div className="p-6 bg-background rounded-lg border border-border">
              <h3 className="text-lg font-semibold text-primary mb-3">
                Nursing Teams
              </h3>
              <p className="text-sm text-muted-foreground">
                Partnership with nursing leadership for operational excellence
              </p>
            </div>
            <div className="p-6 bg-background rounded-lg border border-border">
              <h3 className="text-lg font-semibold text-primary mb-3">
                Technical Teams
              </h3>
              <p className="text-sm text-muted-foreground">
                Engagement with technical and biomedical teams for equipment
                integration
              </p>
            </div>
            <div className="p-6 bg-background rounded-lg border border-border">
              <h3 className="text-lg font-semibold text-primary mb-3">
                Procurement Teams
              </h3>
              <p className="text-sm text-muted-foreground">
                Support for hospital procurement and supply chain management
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Vision Section */}
      <section className="py-16 md:py-24 bg-primary text-primary-foreground">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold font-display mb-6">
            Our Vision
          </h2>
          <p className="text-xl max-w-3xl leading-relaxed mb-8">
            To be recognized as a reliable medical solutions partner trusted by
            healthcare professionals for clinically relevant products and
            professional engagement.
          </p>
          <div className="border-t border-primary-foreground/20 pt-8 mt-8">
            <p className="text-lg italic">Above all Yahweh Rapha</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold font-display text-primary mb-6">
            Interested in Working Together?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Learn more about our products and services, or contact us to discuss
            partnership opportunities
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/products"
              className="px-8 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
            >
              Explore Products
            </Link>
            <Link
              to="/contact"
              className="px-8 py-3 border-2 border-primary text-primary font-semibold rounded-lg hover:bg-primary hover:text-primary-foreground transition-all duration-200"
            >
              Contact Us
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
