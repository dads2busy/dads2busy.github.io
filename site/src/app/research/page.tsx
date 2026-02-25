import CategoryLayout from "@/components/CategoryLayout";
import ResearchPostComponent from "@/components/ResearchPost";
import { getPostsBySubcategory, sortByOrdinal } from "@/lib/content";
import { RESEARCH_SUBCATEGORIES } from "@/lib/constants";
import { ResearchPost } from "@/lib/types";

export default function ResearchPage() {
  return (
    <CategoryLayout category="research">
      {RESEARCH_SUBCATEGORIES.map((subcategory) => {
        const posts = sortByOrdinal(
          getPostsBySubcategory("research", subcategory)
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
