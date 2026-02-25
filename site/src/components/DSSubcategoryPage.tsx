import Link from "next/link";
import DataScienceLayout from "./DataScienceLayout";
import { renderMarkdown } from "@/lib/content";
import { BasePost } from "@/lib/types";

interface Props {
  title: string;
  posts: BasePost[];
}

export default async function DSSubcategoryPage({ title, posts }: Props) {
  const postsWithHtml = await Promise.all(
    posts.map(async (post) => ({
      ...post,
      htmlContent: await renderMarkdown(post.content),
    }))
  );

  return (
    <DataScienceLayout>
      <h2 className="text-xl font-bold mb-4">{title}</h2>
      {postsWithHtml.map((post) => (
        <div key={post.slug} className="mb-6">
          <h4 className="font-bold">
            <Link href={`/${post.year}/${post.month}/${post.slug}`}>
              {post.title}
            </Link>
          </h4>
          {post.htmlContent && (
            <div
              className="post-content text-sm mt-1"
              dangerouslySetInnerHTML={{ __html: post.htmlContent }}
            />
          )}
        </div>
      ))}
    </DataScienceLayout>
  );
}
