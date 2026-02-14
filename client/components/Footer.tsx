import { Link } from "react-router-dom";

const PRODUCT_CATEGORIES = [
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

const QUICK_LINKS = [
  { name: "Home", path: "/" },
  { name: "About Us", path: "/about" },
  { name: "Products", path: "/products" },
  { name: "Services", path: "/services" },
  { name: "Certificates", path: "/certificates" },
  { name: "Careers", path: "/careers" },
];

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-primary text-primary-foreground pt-16 pb-8">
      <div className="container mx-auto px-4">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Column 1: Logo & Tagline */}
          <div>
            <Link to="/" className="block mb-4">
              <img
                src="/logo.jpeg"
                alt="GIMS MEDLINE"
                className="h-12 md:h-16 lg:h-20 w-auto object-contain"
              />
            </Link>
            <p className="text-sm text-primary-foreground/80">
              Clinical excellence through thoughtfully selected medical products
            </p>
          </div>

          {/* Column 2: Quick Links */}
          <div>
            <h4 className="font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              {QUICK_LINKS.map((link) => (
                <li key={link.path}>
                  <Link
                    to={link.path}
                    className="text-sm text-primary-foreground/80 hover:text-primary-foreground transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Column 3: Product Categories */}
          <div>
            <h4 className="font-semibold mb-4">Products</h4>
            <ul className="space-y-2">
              {PRODUCT_CATEGORIES.slice(0, 4).map((category) => (
                <li key={category.path}>
                  <Link
                    to={category.path}
                    className="text-sm text-primary-foreground/80 hover:text-primary-foreground transition-colors"
                  >
                    {category.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Column 4: Contact Details */}
          <div>
            <h4 className="font-semibold mb-4">Contact</h4>
            <div className="text-sm text-primary-foreground/80 space-y-2">
              <p>GIMS MEDLINE</p>
              <p>Healthcare Solutions</p>
              <p>Plot no.19&20, Hanuman Colony,</p>
              <p>Injambakkam, Chennai 600 115.</p>
              <div className="pt-2 space-y-1">
                <p>
                  <a href="tel:+918015873937" className="hover:text-primary-foreground transition-colors">
                    +91 80158 73937
                  </a>
                </p>
                <p>
                  <a href="mailto:info@gimsmedline.com" className="hover:text-primary-foreground transition-colors">
                    info@gimsmedline.com
                  </a>
                </p>
                <p>
                  <a href="mailto:admin@gimsmedline.com" className="hover:text-primary-foreground transition-colors">
                    admin@gimsmedline.com
                  </a>
                </p>
                <p>
                  <a href="http://www.gimsmedline.com" target="_blank" rel="noopener noreferrer" className="hover:text-primary-foreground transition-colors">
                    www.gimsmedline.com
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Strip */}
        <div className="border-t border-primary-foreground/20 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-sm text-primary-foreground/70">
            &copy; {currentYear} GIMS MEDLINE. All rights reserved.
          </p>
          <div className="flex gap-6 text-sm">
            <Link
              to="#"
              className="text-primary-foreground/70 hover:text-primary-foreground transition-colors"
            >
              Privacy Policy
            </Link>
            <Link
              to="#"
              className="text-primary-foreground/70 hover:text-primary-foreground transition-colors"
            >
              Terms
            </Link>
          </div>
        </div>

        {/* Quote Section */}
        <div className="mt-8 text-center">
          <p className="text-sm text-primary-foreground/70 italic">
            Above all Yahweh Rapha
          </p>
        </div>
      </div>
    </footer>
  );
}
