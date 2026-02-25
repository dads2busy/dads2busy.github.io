import CategoryLayout from "@/components/CategoryLayout";
import WritingCitationComponent from "@/components/WritingCitation";
import { getPostsByCategory } from "@/lib/content";
import { WritingPost } from "@/lib/types";

export default function WritingPage() {
  const posts = getPostsByCategory("writing") as WritingPost[];

  // Group by subcategory
  const grouped = new Map<string, WritingPost[]>();
  for (const post of posts) {
    const sub = post.subcategory || "Other";
    if (!grouped.has(sub)) grouped.set(sub, []);
    grouped.get(sub)!.push(post);
  }

  return (
    <CategoryLayout category="writing">
      {Array.from(grouped.entries()).map(([subcategory, subPosts]) => (
        <div key={subcategory}>
          <h3 className="text-lg font-bold border-b border-black pb-1 mb-4 mt-6">
            {subcategory}
          </h3>
          {subPosts.map((post) => (
            <WritingCitationComponent key={post.slug} post={post} />
          ))}
        </div>
      ))}
    </CategoryLayout>
  );
}
