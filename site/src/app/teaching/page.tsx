import Link from "next/link";
import CategoryLayout from "@/components/CategoryLayout";
import { getPostsByCategory, renderMarkdown, truncateContent } from "@/lib/content";

export default async function TeachingPage() {
  const posts = getPostsByCategory("teaching");
  posts.sort((a, b) => b.date.localeCompare(a.date));

  const postsWithHtml = await Promise.all(
    posts.map(async (post) => ({
      ...post,
      htmlContent: await renderMarkdown(post.content),
    }))
  );

  return (
    <CategoryLayout category="teaching">
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
