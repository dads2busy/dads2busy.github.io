import CategoryLayout from "@/components/CategoryLayout";
import SpeakingCitation from "@/components/SpeakingCitation";
import { getPostsByCategory } from "@/lib/content";
import { SpeakingPost } from "@/lib/types";

export default function SpeakingPage() {
  const posts = getPostsByCategory("speaking") as SpeakingPost[];
  posts.sort((a, b) => b.date.localeCompare(a.date));

  // Group by subcategory
  const grouped = new Map<string, SpeakingPost[]>();
  for (const post of posts) {
    const sub = post.subcategory || "Other";
    if (!grouped.has(sub)) grouped.set(sub, []);
    grouped.get(sub)!.push(post);
  }

  return (
    <CategoryLayout category="speaking">
      {Array.from(grouped.entries()).map(([subcategory, subPosts]) => (
        <div key={subcategory}>
          <h3 className="text-lg font-bold border-b border-black pb-1 mb-4 mt-6">
            {subcategory}
          </h3>
          {subPosts.map((post) => (
            <SpeakingCitation key={post.slug} post={post} />
          ))}
        </div>
      ))}
    </CategoryLayout>
  );
}
