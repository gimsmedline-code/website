import { useState } from "react";

export default function Contact() {
  const [formData, setFormData] = useState({
    fullName: "",
    organization: "",
    email: "",
    phone: "",
    // department: "",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setFormData({
        fullName: "",
        organization: "",
        email: "",
        phone: "",
        // department: "",
        message: "",
      });
      setSubmitted(false);
    }, 3000);
  };

  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-primary/5 via-transparent to-accent/5">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold font-display text-primary mb-6">
            Get in Touch
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl">
            We're here to help. Reach out with any questions or inquiries
          </p>
        </div>
      </section>

      {/* Contact Details & Form Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {/* Contact Details */}
            <div>
              <h2 className="text-2xl font-bold font-display text-primary mb-6">
                Contact Details
              </h2>
              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold text-primary mb-2">
                    Company Name
                  </h3>
                  <p className="text-muted-foreground">GIMS MEDLINE</p>
                </div>
                <div>
                  <h3 className="font-semibold text-primary mb-2">
                    Business Type
                  </h3>
                  <p className="text-muted-foreground">Healthcare Solutions</p>
                </div>
                <div>
                  <h3 className="font-semibold text-primary mb-2">
                    Service Areas
                  </h3>
                  <p className="text-muted-foreground">
                    Medical products across multiple specialties
                  </p>
                </div>
              </div>
            </div>

            {/* Contact Form */}
            <div className="md:col-span-2">
              <h2 className="text-2xl font-bold font-display text-primary mb-6">
                Send us a Message
              </h2>

              {submitted ? (
                <div className="bg-accent/10 border border-accent text-accent p-6 rounded-lg mb-8 text-center">
                  <h3 className="font-semibold text-lg mb-2">Thank you!</h3>
                  <p>
                    We've received your message and will be in touch shortly.
                  </p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
                      placeholder="Your name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Hospital / Organization
                    </label>
                    <input
                      type="text"
                      name="organization"
                      value={formData.organization}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
                      placeholder="Organization name"
                    />
                  </div>

                  <div className="grid md:grid-cols-2 gap-5">
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
                        Phone
                      </label>
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        className="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
                        placeholder="+1 (555) 000-0000"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Message *
                    </label>
                    <textarea
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent resize-none"
                      placeholder="Tell us how we can help..."
                      rows={5}
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full px-6 py-3 bg-accent text-accent-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
                  >
                    Send Message
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Map Section */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl md:text-3xl font-bold font-display text-primary mb-8">
            Locate Us
          </h2>
          <div className="w-full h-96 bg-border rounded-lg flex items-center justify-center">
            <div className="text-center">
              <p className="text-muted-foreground mb-4">
                Map integration will be available here
              </p>
              <p className="text-sm text-muted-foreground">
                Contact us directly for location details
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Response Time Notice */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4 max-w-2xl">
          <div className="p-6 bg-gradient-to-br from-accent/10 to-primary/10 border border-border rounded-lg">
            <h3 className="font-semibold text-primary mb-3">
              We're Committed to Timely Response
            </h3>
            <p className="text-muted-foreground text-sm">
              We value your inquiry and aim to respond within 24-48 business
              hours. For urgent matters, please include relevant details in your
              message to help us prioritize your request appropriately.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
