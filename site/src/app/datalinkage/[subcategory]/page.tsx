import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getAllPosts, sortByOrdinal } from "@/lib/content";

const SUBCATEGORIES: Record<string, string> = {
  recordlinkage: "Data Linkage: Entity Resolution",
};

export function generateStaticParams() {
  return Object.keys(SUBCATEGORIES).map((subcategory) => ({ subcategory }));
}

export default async function DataLinkageSubPage({
  params,
}: {
  params: Promise<{ subcategory: string }>;
}) {
  const { subcategory } = await params;
  const title = SUBCATEGORIES[subcategory] || subcategory;

  const posts = sortByOrdinal(
    getAllPosts().filter(
      (p) => p.category?.toLowerCase() === "datalinkage"
    )
  );

  return <DSSubcategoryPage title={title} posts={posts} />;
}
