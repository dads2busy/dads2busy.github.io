export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="fixed bottom-0 left-0 right-0 z-50 bg-neutral-900 border-t border-neutral-700 py-2 text-center text-sm text-gray-400">
      &copy; {year} Aaron Schroeder. Powered by{" "}
      <a href="https://nextjs.org" className="text-red-400 hover:text-pink-400">
        Next.js
      </a>
    </footer>
  );
}
