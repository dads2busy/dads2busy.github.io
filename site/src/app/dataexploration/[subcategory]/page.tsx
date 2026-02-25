import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getAllPosts, sortByOrdinal } from "@/lib/content";

const SUBCATEGORIES: Record<string, string> = {
  characterization: "Data Exploration: Characterization",
};

export function generateStaticParams() {
  return Object.keys(SUBCATEGORIES).map((subcategory) => ({ subcategory }));
}

export default async function DataExplorationSubPage({
  params,
}: {
  params: Promise<{ subcategory: string }>;
}) {
  const { subcategory } = await params;
  const title = SUBCATEGORIES[subcategory] || subcategory;

  const posts = sortByOrdinal(
    getAllPosts().filter(
      (p) => p.category?.toLowerCase() === "dataexploration"
    )
  );

  return <DSSubcategoryPage title={title} posts={posts} />;
}
