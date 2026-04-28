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

  // Sort each subcategory's entries by year descending (use full date if available)
  for (const subPosts of grouped.values()) {
    subPosts.sort((a, b) => {
      const yearA = a.dates || (a.date ? a.date.slice(0, 4) : "0");
      const yearB = b.dates || (b.date ? b.date.slice(0, 4) : "0");
      return String(yearB).localeCompare(String(yearA));
    });
  }

  const entries = Array.from(grouped.entries());
  const journalIndex = entries.findIndex(
    ([subcategory]) => subcategory === "Journal Publications (refereed)",
  );
  if (journalIndex > 0) {
    const [journalEntry] = entries.splice(journalIndex, 1);
    entries.unshift(journalEntry);
  }


  return (
    <CategoryLayout category="writing">
      {entries.map(([subcategory, subPosts]) => (
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
