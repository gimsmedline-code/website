import { useState } from "react";
import { toast } from "sonner";

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
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          access_key: "902fc6fa-d2a6-4d90-ba35-9f459b4ebc99",
          ...formData,
        }),
      });

      const result = await response.json();

      if (result.success) {
        setSubmitted(true);
        toast.success("Message sent successfully!");
        setFormData({
          fullName: "",
          organization: "",
          email: "",
          phone: "",
          // department: "",
          message: "",
        });
        setTimeout(() => setSubmitted(false), 5000);
      } else {
        toast.error(result.message || "Something went wrong. Please try again.");
      }
    } catch (error) {
      toast.error("Failed to send message. Please try again later.");
      console.error("Form submission error:", error);
    } finally {
      setIsSubmitting(false);
    }
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
                    Address
                  </h3>
                  <p className="text-muted-foreground">
                    Plot no.19&20, Hanuman Colony,
                    <br />
                    Injambakkam, Chennai 600 115.
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold text-primary mb-2">
                    Phone
                  </h3>
                  <p className="text-muted-foreground">
                    <a href="tel:+918015873937" className="hover:text-primary transition-colors">
                      +91 80158 73937
                    </a>
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold text-primary mb-2">
                    Email
                  </h3>
                  <div className="text-muted-foreground space-y-1">
                    <p>
                      <a href="mailto:info@gimsmedline.com" className="hover:text-primary transition-colors">
                        info@gimsmedline.com
                      </a>
                    </p>
                    <p>
                      <a href="mailto:admin@gimsmedline.com" className="hover:text-primary transition-colors">
                        admin@gimsmedline.com
                      </a>
                    </p>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold text-primary mb-2">
                    Website
                  </h3>
                  <p className="text-muted-foreground">
                    <a href="http://www.gimsmedline.com" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">
                      www.gimsmedline.com
                    </a>
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold text-primary mb-2">
                    Business Hours
                  </h3>
                  <p className="text-muted-foreground">
                    Mon - Sat: 9:00 AM - 6:00 PM
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
                    disabled={isSubmitting}
                    className="w-full px-6 py-3 bg-accent text-accent-foreground font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? "Sending..." : "Send Message"}
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
          <div className="w-full h-96 bg-border rounded-lg overflow-hidden shadow-lg">
            <iframe
              src="https://maps.google.com/maps?q=Hanuman%20Colony,%20Injambakkam,%20Chennai&t=&z=13&ie=UTF8&iwloc=&output=embed"
              width="100%"
              height="100%"
              style={{ border: 0 }}
              allowFullScreen
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
            ></iframe>
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
