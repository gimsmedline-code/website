import { useState } from "react";
import { Link } from "react-router-dom";

export default function Careers() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    message: "",
  });
  const [fileName, setFileName] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFileName(e.target.files[0].name);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setFormData({ name: "", email: "", phone: "", message: "" });
      setFileName(null);
      setSubmitted(false);
    }, 3000);
  };

  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-primary/5 via-transparent to-accent/5">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold font-display text-primary mb-6">
            Join Our Team
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl">
            Be part of a team committed to clinical excellence and healthcare
            advancement
          </p>
        </div>
      </section>

      {/* Introduction Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl">
            <p className="text-xl text-foreground leading-relaxed mb-8">
              At GIMS MEDLINE, we're building a team of dedicated professionals
              who share our commitment to clinical excellence and healthcare
              innovation. If you're passionate about making a difference in
              healthcare, we want to hear from you.
            </p>

            <h2 className="text-2xl md:text-3xl font-bold font-display text-primary mb-6">
              Why Join GIMS MEDLINE?
            </h2>
            <ul className="space-y-4">
              <li className="flex items-start gap-4">
                <span className="flex-shrink-0 w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
                  <span className="text-accent font-bold text-sm">✓</span>
                </span>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">
                    Mission-Driven Work
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Contribute to improving healthcare outcomes
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-4">
                <span className="flex-shrink-0 w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
                  <span className="text-accent font-bold text-sm">✓</span>
                </span>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">
                    Professional Growth
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Develop expertise in healthcare and medical devices
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-4">
                <span className="flex-shrink-0 w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
                  <span className="text-accent font-bold text-sm">✓</span>
                </span>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">
                    Collaborative Culture
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Work with a team that values expertise and integrity
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-4">
                <span className="flex-shrink-0 w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
                  <span className="text-accent font-bold text-sm">✓</span>
                </span>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Impact</h3>
                  <p className="text-sm text-muted-foreground">
                    Be part of decisions that shape healthcare solutions
                  </p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Current Openings Section */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl md:text-3xl font-bold font-display text-primary mb-8">
            Current Openings
          </h2>
          <div className="bg-white p-8 rounded-lg border border-border text-center">
            <p className="text-muted-foreground mb-4">
              We're always looking for talented professionals. Check back
              regularly for new opportunities or submit your resume below to be
              considered for future positions.
            </p>
          </div>
        </div>
      </section>

      {/* Resume Upload Form Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold font-display text-primary mb-8">
              Submit Your Resume
            </h2>

            {submitted ? (
              <div className="bg-accent/10 border border-accent text-accent p-6 rounded-lg mb-8 text-center">
                <h3 className="font-semibold text-lg mb-2">Thank you!</h3>
                <p>
                  We've received your submission and will review it shortly.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
                    placeholder="Your name"
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Email *
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
                      placeholder="your@email.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Phone *
                    </label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
                      placeholder="+1 (555) 000-0000"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Resume Upload *
                  </label>
                  <label className="flex items-center justify-center w-full p-6 border-2 border-dashed border-border rounded-lg hover:border-accent hover:bg-background transition-colors cursor-pointer">
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileChange}
                      required
                      className="hidden"
                    />
                    <div className="text-center">
                      <p className="text-sm font-medium text-foreground">
                        {fileName
                          ? `Selected: ${fileName}`
                          : "Click to upload your resume"}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        PDF, DOC, or DOCX
                      </p>
                    </div>
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Message (Optional)
                  </label>
                  <textarea
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent resize-none"
                    placeholder="Tell us about yourself or any relevant experience..."
                    rows={5}
                  />
                </div>

                <button
                  type="submit"
                  className="w-full px-6 py-3 bg-accent text-accent-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
                >
                  Submit Resume
                </button>
              </form>
            )}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-16 md:py-24 bg-primary text-primary-foreground text-center">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl md:text-3xl font-bold font-display mb-4">
            Questions?
          </h2>
          <p className="mb-6 max-w-2xl mx-auto">
            Reach out to our team to learn more about career opportunities at
            GIMS MEDLINE
          </p>
          <Link
            to="/contact"
            className="inline-block px-8 py-3 bg-accent text-accent-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
          >
            Contact Us
          </Link>
        </div>
      </section>
    </div>
  );
}
