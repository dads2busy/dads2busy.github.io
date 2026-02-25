import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getAllPosts, sortByOrdinal } from "@/lib/content";

const SUBCATEGORIES: Record<string, string> = {
  fitnessforuse: "Data Fitness: Fitness for Use",
};

export function generateStaticParams() {
  return Object.keys(SUBCATEGORIES).map((subcategory) => ({ subcategory }));
}

export default async function DataFitnessSubPage({
  params,
}: {
  params: Promise<{ subcategory: string }>;
}) {
  const { subcategory } = await params;
  const title = SUBCATEGORIES[subcategory] || subcategory;

  const posts = sortByOrdinal(
    getAllPosts().filter(
      (p) => p.category?.toLowerCase() === "datafitness"
    )
  );

  return <DSSubcategoryPage title={title} posts={posts} />;
}
