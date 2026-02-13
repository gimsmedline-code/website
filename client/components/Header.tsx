import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { Menu, X } from "lucide-react";

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

const MAIN_LINKS = [
  { name: "Home", path: "/" },
  { name: "About Us", path: "/about" },
  { name: "Products", path: "/products" },
  { name: "Services", path: "/services" },
  { name: "Certificates", path: "/certificates" },
  { name: "Careers", path: "/careers" },
  { name: "Contact Us", path: "/contact" },
];

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [productsDropdownOpen, setProductsDropdownOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string) =>
    location.pathname === path || location.pathname.startsWith(path + "/");

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center gap-2"
          >
            <img
              src="/logo.jpeg"
              alt="GIMS MEDLINE"
              className="h-20 w-auto object-contain"
            />
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {MAIN_LINKS.map((link) => (
              <div key={link.path} className="relative group">
                <Link
                  to={link.path}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${isActive(link.path)
                      ? "text-primary"
                      : "text-foreground hover:text-primary"
                    }`}
                >
                  {link.name}
                </Link>

                {/* Products Dropdown */}
                {link.name === "Products" && (
                  <div className="absolute left-0 mt-0 w-56 bg-white border border-border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    {PRODUCT_CATEGORIES.map((category) => (
                      <Link
                        key={category.path}
                        to={category.path}
                        className="block px-4 py-3 text-sm text-foreground hover:text-primary hover:bg-background transition-colors first:rounded-t-lg last:rounded-b-lg"
                      >
                        {category.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>

          {/* Right CTA Button */}
          <div className="hidden md:flex items-center">
            <Link
              to="/contact"
              className="px-6 py-2.5 bg-accent text-accent-foreground rounded-lg font-medium text-sm hover:bg-opacity-90 transition-all duration-200 hover:shadow-lg"
            >
              Enquire Now
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-foreground"
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden pb-4">
            {MAIN_LINKS.map((link) => (
              <div key={link.path}>
                {link.name === "Products" ? (
                  <>
                    <button
                      onClick={() =>
                        setProductsDropdownOpen(!productsDropdownOpen)
                      }
                      className="w-full text-left px-4 py-3 text-sm font-medium text-foreground hover:text-primary hover:bg-background transition-colors"
                    >
                      {link.name}
                    </button>
                    {productsDropdownOpen && (
                      <div className="bg-background pl-4">
                        {PRODUCT_CATEGORIES.map((category) => (
                          <Link
                            key={category.path}
                            to={category.path}
                            onClick={() => {
                              setMobileMenuOpen(false);
                              setProductsDropdownOpen(false);
                            }}
                            className="block px-4 py-2 text-sm text-foreground hover:text-primary"
                          >
                            {category.name}
                          </Link>
                        ))}
                      </div>
                    )}
                  </>
                ) : (
                  <Link
                    to={link.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`block px-4 py-3 text-sm font-medium transition-colors ${isActive(link.path)
                        ? "text-primary bg-background"
                        : "text-foreground hover:text-primary hover:bg-background"
                      }`}
                  >
                    {link.name}
                  </Link>
                )}
              </div>
            ))}
            <Link
              to="/contact"
              onClick={() => setMobileMenuOpen(false)}
              className="m-4 block px-6 py-2.5 bg-accent text-accent-foreground rounded-lg font-medium text-sm text-center hover:bg-opacity-90 transition-all"
            >
              Enquire Now
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
}
