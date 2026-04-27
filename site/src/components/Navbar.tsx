"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { NAV_ITEMS, SITE_NAME } from "@/lib/constants";

export default function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50"
      style={{
        background: "var(--nav-bg)",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
      }}
    >
      <div className="max-w-5xl mx-auto px-4 flex items-center justify-between h-14">
        <Link
          href="/"
          style={{
            fontFamily: "var(--font-display)",
            color: "var(--nav-active)",
            fontSize: "1.5rem",
            lineHeight: 1,
            textDecoration: "none",
          }}
        >
          {SITE_NAME}
        </Link>

        {/* Hamburger */}
        <button
          className="md:hidden p-2"
          style={{ color: "var(--nav-text)" }}
          onClick={() => setOpen(!open)}
          aria-label="Toggle navigation"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            {open ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            )}
          </svg>
        </button>

        {/* Desktop nav */}
        <ul className="hidden md:flex items-center gap-1">
          {NAV_ITEMS.map((item) => {
            const active = !item.external && pathname.startsWith(item.href);
            return (
              <li key={item.href}>
                <NavLink item={item} active={active} />
              </li>
            );
          })}
        </ul>
      </div>

      {/* Mobile nav */}
      {open && (
        <ul
          className="md:hidden px-4 pb-4"
          style={{
            background: "var(--nav-bg)",
            borderTop: "1px solid rgba(255,255,255,0.06)",
          }}
        >
          {NAV_ITEMS.map((item) => (
            <li key={item.href}>
              {item.external ? (
                <a
                  href={item.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block py-2 text-sm"
                  style={{ color: "var(--nav-text)" }}
                  onClick={() => setOpen(false)}
                >
                  {item.label}
                </a>
              ) : (
                <Link
                  href={item.href}
                  className="block py-2 text-sm"
                  style={{ color: "var(--nav-text)" }}
                  onClick={() => setOpen(false)}
                >
                  {item.label}
                </Link>
              )}
            </li>
          ))}
        </ul>
      )}
    </nav>
  );
}

function NavLink({
  item,
  active,
}: {
  item: { label: string; href: string; external?: boolean };
  active: boolean;
}) {
  const baseStyle: React.CSSProperties = {
    fontSize: "0.8125rem",
    color: active ? "var(--nav-active)" : "var(--nav-text)",
    textDecoration: "none",
    transition: "color var(--transition)",
  };
  const onEnter = (e: React.MouseEvent<HTMLElement>) => {
    (e.currentTarget as HTMLElement).style.color = "var(--nav-hover)";
  };
  const onLeave = (e: React.MouseEvent<HTMLElement>) => {
    (e.currentTarget as HTMLElement).style.color = active
      ? "var(--nav-active)"
      : "var(--nav-text)";
  };

  if (item.external) {
    return (
      <a
        href={item.href}
        target="_blank"
        rel="noopener noreferrer"
        className="px-3 py-2"
        style={baseStyle}
        onMouseEnter={onEnter}
        onMouseLeave={onLeave}
      >
        {item.label}
      </a>
    );
  }
  return (
    <Link
      href={item.href}
      className="px-3 py-2"
      style={baseStyle}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
    >
      {item.label}
    </Link>
  );
}
