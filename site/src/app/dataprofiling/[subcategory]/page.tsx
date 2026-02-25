import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getAllPosts, sortByOrdinal } from "@/lib/content";

const SUBCATEGORIES: Record<string, string> = {
  dataquality: "Data Profiling: Quality",
  datastructure: "Data Profiling: Structure",
  metadata: "Data Profiling: Metadata",
};

export function generateStaticParams() {
  return Object.keys(SUBCATEGORIES).map((subcategory) => ({ subcategory }));
}

export default async function DataProfilingSubPage({
  params,
}: {
  params: Promise<{ subcategory: string }>;
}) {
  const { subcategory } = await params;
  const title = SUBCATEGORIES[subcategory] || subcategory;

  const posts = sortByOrdinal(
    getAllPosts().filter(
      (p) =>
        p.category?.toLowerCase() === "dataprofiling" &&
        p.subcategory?.toLowerCase().replace(/\s+/g, "").includes(subcategory.replace("data", ""))
    )
  );

  return <DSSubcategoryPage title={title} posts={posts} />;
}
