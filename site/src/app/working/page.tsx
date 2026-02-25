import { getPostsByCategory, sortByOrdinal, renderMarkdown } from "@/lib/content";
import { WorkingPost } from "@/lib/types";
import CategoryLayout from "@/components/CategoryLayout";

export default async function WorkingPage() {
  const posts = sortByOrdinal(getPostsByCategory("working")) as WorkingPost[];

  const postsWithHtml = await Promise.all(
    posts.map(async (post) => ({
      ...post,
      htmlContent: await renderMarkdown(post.content),
    }))
  );

  return (
    <CategoryLayout category="working">
      {postsWithHtml.map((post) => (
        <div key={post.slug} className="mb-8">
          <h3 className="text-lg font-bold">{post.title}</h3>
          {post.subtitle && (
            <h4 className="text-sm text-gray-600 mt-1">{post.subtitle}</h4>
          )}
          {post.dates && (
            <p className="text-sm text-gray-500 mt-1">{post.dates}</p>
          )}
          {post.htmlContent && (
            <div
              className="post-content text-sm mt-2"
              dangerouslySetInnerHTML={{ __html: post.htmlContent }}
            />
          )}
        </div>
      ))}
    </CategoryLayout>
  );
}
