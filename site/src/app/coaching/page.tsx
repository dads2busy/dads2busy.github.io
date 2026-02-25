import Link from "next/link";
import CategoryLayout from "@/components/CategoryLayout";
import { getPostsByCategory, sortByOrdinal, renderMarkdown, truncateContent } from "@/lib/content";

export default async function CoachingPage() {
  const posts = sortByOrdinal(getPostsByCategory("coaching"));

  const postsWithHtml = await Promise.all(
    posts.map(async (post) => ({
      ...post,
      htmlContent: await renderMarkdown(post.content),
    }))
  );

  return (
    <CategoryLayout category="coaching">
      {postsWithHtml.map((post) => (
        <div key={post.slug} className="mb-6">
          <h3 className="text-lg font-bold">
            <Link href={`/${post.year}/${post.month}/${post.slug}`}>
              {post.title}
            </Link>
          </h3>
          {post.htmlContent && (
            <p className="text-sm mt-1">
              {truncateContent(post.htmlContent, 100)}
            </p>
          )}
        </div>
      ))}
    </CategoryLayout>
  );
}
