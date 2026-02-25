import Link from "next/link";
import { getPostsByCategory } from "@/lib/content";
import { GuitarPost } from "@/lib/types";

export default function GuitarPage() {
  const posts = getPostsByCategory("guitar") as GuitarPost[];
  posts.sort((a, b) => (a.artist || "").localeCompare(b.artist || ""));

  return (
    <div className="flex flex-col md:flex-row gap-6">
      {/* Sidebar */}
      <aside className="md:w-1/4">
        <img
          src="/images/TikiHutGuitar.jpg"
          alt="Guitar"
          className="w-52 mb-5"
        />
        <div className="well sidebar">
          <h5 className="font-bold text-sm mb-2">
            Some Self-Teaching Tools I&apos;ve Created
          </h5>
          <ul className="list-none p-0 text-sm">
            <li className="mt-1">
              <a href="/downloads/Open and Neck Chords in a Key - 6th String Root.pdf">
                Open and Neck Chords in a Key - 6th String Root
              </a>
            </li>
            <li className="mt-1">
              <a href="/downloads/Open and Neck Chords in a Key - 5th String Root.pdf">
                Open and Neck Chords in a Key - 5th String Root
              </a>
            </li>
            <li className="mt-1">
              <a href="/downloads/Music_Theory_101.pdf">Music Theory 101</a>
            </li>
          </ul>
        </div>
      </aside>

      {/* Main content */}
      <div className="w-full md:w-3/4">
        {/* Sub-nav */}
        <nav className="mb-4">
          <ul className="flex gap-0 bg-black rounded">
            <li>
              <Link
                href="/guitar"
                className="block px-4 py-2 text-sm text-white hover:text-pink-300"
              >
                Guitar
              </Link>
            </li>
            <li>
              <span className="block px-4 py-2 text-sm text-gray-500">
                Hovercraft
              </span>
            </li>
            <li>
              <span className="block px-4 py-2 text-sm text-gray-500">
                Sailing
              </span>
            </li>
            <li>
              <span className="block px-4 py-2 text-sm text-gray-500">
                Photography
              </span>
            </li>
          </ul>
        </nav>

        <h5 className="font-bold text-sm mb-1">
          Songs I Can Kinda Play-n-Sing
        </h5>
        <p className="text-xs text-gray-500 mb-4">
          I&apos;m Available For Any And All Tiki Hut Jam Sessions!
        </p>

        <table className="text-sm w-full max-w-lg">
          <thead>
            <tr className="border-b">
              <th className="text-left py-1">Song</th>
              <th className="text-left py-1">Artist</th>
            </tr>
          </thead>
          <tbody>
            {posts.map((post) => (
              <tr key={post.slug} className="border-b border-gray-100">
                <td className="py-1">
                  {post.file && post.file.trim() !== "" ? (
                    <a href={`/downloads/chords/${post.file}`}>{post.title}</a>
                  ) : (
                    post.title
                  )}
                </td>
                <td className="py-1">{post.artist}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
