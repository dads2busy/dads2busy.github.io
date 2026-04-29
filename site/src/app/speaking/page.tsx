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

  const CATEGORY_ORDER = [
    "Panelist",
    "Presentations/Workshops",
    "Committee",
    "Lecture",
    "Expert Forum",
    "Expert Webinar",
  ];

  // Sort each group by date DESC
  for (const subPosts of grouped.values()) {
    subPosts.sort((a, b) => (b.date || "").localeCompare(a.date || ""));
  }

  // Order the entries by CATEGORY_ORDER (any unknown categories fall to the end)
  const orderedEntries = [
    ...CATEGORY_ORDER.map((cat) => [cat, grouped.get(cat)] as const).filter(
      ([, posts]) => posts && posts.length > 0,
    ),
    ...Array.from(grouped.entries()).filter(
      ([cat]) => !CATEGORY_ORDER.includes(cat),
    ),
  ] as Array<readonly [string, SpeakingPost[]]>;

  return (
    <CategoryLayout category="speaking">
      {orderedEntries.map(([subcategory, subPosts]) => (
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
