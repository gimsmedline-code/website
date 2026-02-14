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
          <div className="max-w-4xl">
            <p className="text-xl text-foreground mb-8 leading-relaxed">
              GIMS MEDLINE is a healthcare solutions organization dedicated to strengthening modern clinical practice through a thoughtfully curated portfolio of medical devices and disposables. We operate with a clear understanding that healthcare institutions require more than product availability. They require reliability, regulatory assurance, and solutions that seamlessly integrate into established clinical workflows.
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
            {/* Left Column: Approach & Dependability */}
            <div>
              <h3 className="text-xl font-semibold text-primary mb-6">
                Our Approach
              </h3>
              <div className="space-y-6 text-muted-foreground leading-relaxed">
                <p>
                  Our approach is rooted in supporting clinical excellence. Every product is selected with careful attention to quality standards, material integrity, sterility assurance, and consistent performance in real-world hospital environments. We serve key therapeutic specialties including Cardiothoracic, Interventional Radiology, Critical Care, providing solutions that contribute to diagnostic precision, procedural efficiency, and enhanced patient safety.
                </p>
                <p>
                  Beyond product selection, GIMS MEDLINE places strong emphasis on operational dependability. We recognize that in healthcare, timely availability directly impacts patient care. Our logistics and supply processes are structured to ensure dependable and on-time delivery, enabling hospitals and healthcare providers to maintain uninterrupted clinical operations.
                </p>
              </div>
            </div>

            {/* Right Column: Sourcing & Vision (Product Standards) */}
            <div className="bg-gradient-to-br from-primary/10 to-accent/10 p-8 rounded-lg">
              <h3 className="text-xl font-semibold text-primary mb-6">
                Product Standards & Strategy
              </h3>
              <div className="space-y-6">
                <p className="text-foreground leading-relaxed">
                  Our sourcing strategy combines partnerships with established domestic manufacturers and internationally recognized brands. By integrating both locally manufactured and imported products that meet applicable regulatory and international certification standards, we provide access to technologies aligned with evolving global healthcare benchmarks.
                </p>
                <p className="text-foreground leading-relaxed">
                  As healthcare requirements continue to advance, we remain agile in expanding and refining our portfolio. Our objective is to serve as a reliable distribution partner, delivering medical solutions that uphold clinical standards, support institutional efficiency, and contribute meaningfully to improved patient outcomes.
                </p>
                <div className="pt-6 border-t border-border">
                  <p className="text-lg font-serif italic text-primary font-medium text-center bg-white/50 p-4 rounded-lg shadow-sm">
                    "At GIMS MEDLINE, precision in product selection, integrity in operations, and commitment to timely service define the foundation of our work."
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quality & Certifications Section */}
      <section className="py-16 md:py-24 bg-secondary/30">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold font-display text-primary mb-12 text-center">
            Commitment to Quality & Standards
          </h2>
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div className="p-8 bg-white border border-border rounded-lg shadow-sm hover:shadow-md transition-all duration-300">
              <div className="w-20 h-20 mx-auto bg-accent/10 rounded-full flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-accent">ISO</span>
              </div>
              <h3 className="text-xl font-semibold text-primary mb-3">
                ISO 13485:2016
              </h3>
              <p className="text-muted-foreground">
                Certified for Medical Devices Quality Management Systems, ensuring
                consistent design, development, and production.
              </p>
            </div>
            <div className="p-8 bg-white border border-border rounded-lg shadow-sm hover:shadow-md transition-all duration-300">
              <div className="w-20 h-20 mx-auto bg-accent/10 rounded-full flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-accent">CE</span>
              </div>
              <h3 className="text-xl font-semibold text-primary mb-3">
                CE Certified
              </h3>
              <p className="text-muted-foreground">
                Products compliant with European health, safety, and environmental
                protection standards for medical devices.
              </p>
            </div>
            <div className="p-8 bg-white border border-border rounded-lg shadow-sm hover:shadow-md transition-all duration-300">
              <div className="w-20 h-20 mx-auto bg-accent/10 rounded-full flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-accent">GMP</span>
              </div>
              <h3 className="text-xl font-semibold text-primary mb-3">
                WHO GMP
              </h3>
              <p className="text-muted-foreground">
                Manufacturing practices adhering to Good Manufacturing Practice
                guidelines ensuring consistent quality standards.
              </p>
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
