import CategoryLayout from "@/components/CategoryLayout";
import ResearchPostComponent from "@/components/ResearchPost";
import { getPostsBySubcategory } from "@/lib/content";
import { RESEARCH_SUBCATEGORIES } from "@/lib/constants";
import { ResearchPost } from "@/lib/types";

export default function ResearchPage() {
  return (
    <CategoryLayout category="research">
      {RESEARCH_SUBCATEGORIES.map((subcategory) => {
        const posts = getPostsBySubcategory("research", subcategory).sort(
          (a, b) => {
            const dateCompare = b.date.localeCompare(a.date);
            if (dateCompare !== 0) return dateCompare;
            return (a.ordinal ?? 999) - (b.ordinal ?? 999);
          },
        ) as ResearchPost[];
        if (posts.length === 0) return null;
        return (
          <div key={subcategory}>
            <h3 className="text-lg font-bold border-b border-black pb-1 mb-4 mt-6">
              {subcategory}
            </h3>
            {posts.map((post) => (
              <ResearchPostComponent key={post.slug} post={post} />
            ))}
          </div>
        );
      })}
    </CategoryLayout>
  );
}
