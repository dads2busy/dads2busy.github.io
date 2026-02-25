import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getPostsByCategory, sortByOrdinal } from "@/lib/content";

export default async function MacSetupPage() {
  const posts = sortByOrdinal(getPostsByCategory("macsetup"));
  return <DSSubcategoryPage title="Mac Setup" posts={posts} />;
}
