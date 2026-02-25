import Link from "next/link";
import { getAllPosts } from "@/lib/content";

export default function ArchivePage() {
  const posts = getAllPosts();
  posts.sort((a, b) => b.date.localeCompare(a.date));

  // Group by year
  const byYear = new Map<string, typeof posts>();
  for (const post of posts) {
    const year = post.year;
    if (!byYear.has(year)) byYear.set(year, []);
    byYear.get(year)!.push(post);
  }

  return (
    <div className="well">
      <h2 className="text-2xl font-bold mb-6">Archive</h2>
      {Array.from(byYear.entries())
        .sort(([a], [b]) => b.localeCompare(a))
        .map(([year, yearPosts]) => (
          <div key={year} className="mb-6">
            <h3 className="text-lg font-bold border-b border-gray-300 pb-1 mb-2">
              {year}
            </h3>
            <ul className="space-y-1">
              {yearPosts.map((post) => (
                <li key={`${post.year}-${post.month}-${post.slug}`} className="text-sm">
                  <span className="text-gray-500 mr-2">{post.date}</span>
                  <Link href={`/${post.year}/${post.month}/${post.slug}`}>
                    {post.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
    </div>
  );
}
