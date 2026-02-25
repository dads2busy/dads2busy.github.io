import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getAllPosts, sortByOrdinal } from "@/lib/content";

const SUBCATEGORIES: Record<string, { category: string; title: string }> = {
  identification: { category: "datadiscovery", title: "Data Discovery: Identification" },
  screening: { category: "datadiscovery", title: "Data Discovery: Screening" },
  inventory: { category: "datadiscovery", title: "Data Discovery: Inventory" },
  access: { category: "datadiscovery", title: "Data Discovery: Data Access" },
};

export function generateStaticParams() {
  return Object.keys(SUBCATEGORIES).map((subcategory) => ({ subcategory }));
}

export default async function DataDiscoverySubPage({
  params,
}: {
  params: Promise<{ subcategory: string }>;
}) {
  const { subcategory } = await params;
  const info = SUBCATEGORIES[subcategory];
  if (!info) return <div>Not found</div>;

  const posts = sortByOrdinal(
    getAllPosts().filter(
      (p) =>
        p.category?.toLowerCase() === info.category.toLowerCase() ||
        p.subcategory?.toLowerCase().includes(subcategory)
    )
  );

  return <DSSubcategoryPage title={info.title} posts={posts} />;
}
