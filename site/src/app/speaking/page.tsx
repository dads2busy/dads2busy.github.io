import Link from "next/link";
import CategoryLayout from "@/components/CategoryLayout";
import { getPostsByCategory, renderMarkdown, truncateContent } from "@/lib/content";
import { SpeakingPost } from "@/lib/types";

export default async function SpeakingPage() {
  const posts = getPostsByCategory("speaking") as SpeakingPost[];
  posts.sort((a, b) => b.date.localeCompare(a.date));

  const postsWithHtml = await Promise.all(
    posts.map(async (post) => ({
      ...post,
      htmlContent: await renderMarkdown(post.content),
    }))
  );

  return (
    <CategoryLayout category="speaking">
      {postsWithHtml.map((post) => (
        <div key={post.slug} className="mb-6">
          <h4 className="font-bold">
            <Link href={`/${post.year}/${post.month}/${post.slug}`}>
              {post.title || post.content.trim().slice(0, 80)}
            </Link>
          </h4>
          <p className="text-xs text-gray-500 mb-1">{post.date}</p>
          {post.htmlContent && (
            <p className="text-sm">
              {truncateContent(post.htmlContent, 100)}
            </p>
          )}
          {post.report && post.report.trim() !== "" && (
            <p className="text-sm mt-1">
              <a href={`/downloads/${post.report}`}>Download Report</a>
            </p>
          )}
        </div>
      ))}
    </CategoryLayout>
  );
}
