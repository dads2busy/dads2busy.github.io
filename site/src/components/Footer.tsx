import Link from "next/link";
import { NAV_ITEMS, SITE_NAME } from "@/lib/constants";

export default function Footer() {
  const year = new Date().getFullYear();
  const half = Math.ceil(NAV_ITEMS.length / 2);
  const colA = NAV_ITEMS.slice(0, half);
  const colB = NAV_ITEMS.slice(half);

  return (
    <footer
      className="mt-16"
      style={{
        background: "var(--nav-bg)",
        color: "var(--nav-text)",
      }}
    >
      <div className="max-w-5xl mx-auto px-4 py-10 grid gap-8 md:grid-cols-3 text-sm">
        {/* Affiliation */}
        <div>
          <p
            style={{
              fontFamily: "var(--font-display)",
              color: "var(--nav-active)",
              fontSize: "1.5rem",
              lineHeight: 1.1,
              marginBottom: "0.5rem",
            }}
          >
            {SITE_NAME}
          </p>
          <p style={{ color: "var(--nav-text)" }}>
            Aaron D. Schroeder, Ph.D.
            <br />
            Research Associate Professor
            <br />
            Social &amp; Decision Analytics Division
            <br />
            University of Virginia Biocomplexity Institute
          </p>
          <p className="mt-3">
            <a
              href="mailto:aaron.schroeder@virginia.edu"
              style={{ color: "var(--nav-active)" }}
            >
              aaron.schroeder@virginia.edu
            </a>
          </p>
          <p className="mt-2 text-sm">
            <a
              href="/vita.pdf"
              style={{ color: "var(--nav-active)" }}
            >
              Curriculum Vitae (PDF)
            </a>
          </p>
        </div>

        {/* Nav links */}
        <div className="md:col-span-2 grid grid-cols-2 gap-x-6 gap-y-2">
          {[colA, colB].map((col, i) => (
            <ul key={i} className="space-y-2">
              {col.map((item) =>
                item.external ? (
                  <li key={item.href}>
                    <a
                      href={item.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: "var(--nav-text)" }}
                      className="hover:underline"
                    >
                      {item.label}
                    </a>
                  </li>
                ) : (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      style={{ color: "var(--nav-text)" }}
                      className="hover:underline"
                    >
                      {item.label}
                    </Link>
                  </li>
                )
              )}
            </ul>
          ))}
        </div>
      </div>

      <div
        className="border-t"
        style={{ borderColor: "rgba(255,255,255,0.06)" }}
      >
        <div
          className="max-w-5xl mx-auto px-4 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-2 text-xs"
          style={{ color: "var(--nav-text)" }}
        >
          <p>&copy; {year} Aaron Schroeder.</p>
          <p>
            Content licensed under{" "}
            <a
              href="https://creativecommons.org/licenses/by/4.0/"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "var(--nav-active)" }}
            >
              CC BY 4.0
            </a>
            . Built with{" "}
            <a
              href="https://nextjs.org"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "var(--nav-active)" }}
            >
              Next.js
            </a>
            .
          </p>
        </div>
      </div>
    </footer>
  );
}
