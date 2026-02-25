import { getAllPostSlugs, getPostBySlug, renderMarkdown } from "@/lib/content";
import { DS_CATEGORIES } from "@/lib/constants";
import CategoryLayout from "@/components/CategoryLayout";
import DataScienceLayout from "@/components/DataScienceLayout";

export function generateStaticParams() {
  return getAllPostSlugs();
}

export default async function PostPage({
  params,
}: {
  params: Promise<{ year: string; month: string; slug: string }>;
}) {
  const { year, month, slug } = await params;
  const post = getPostBySlug(year, month, slug);

  if (!post) {
    return <div className="text-center py-12">Post not found.</div>;
  }

  const htmlContent = await renderMarkdown(post.content);
  const isDsCategory = DS_CATEGORIES.includes(post.category?.toLowerCase());

  const content = (
    <article>
      <h2 className="text-2xl font-bold mb-2">{post.title}</h2>
      {post.website && post.website.trim() !== "" && (
        <p className="text-sm mb-3">
          <a href={post.website} target="_blank" rel="noopener noreferrer">
            View Website
          </a>
        </p>
      )}
      {htmlContent && (
        <div
          className="post-content"
          dangerouslySetInnerHTML={{ __html: htmlContent }}
        />
      )}
    </article>
  );

  if (isDsCategory) {
    return <DataScienceLayout>{content}</DataScienceLayout>;
  }

  return (
    <CategoryLayout category={post.category || "default"}>
      {content}
    </CategoryLayout>
  );
}
