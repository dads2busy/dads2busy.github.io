import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getPostsByCategory, sortByOrdinal } from "@/lib/content";

export default async function AuthConfigPage() {
  const posts = sortByOrdinal(getPostsByCategory("authconfig"));
  return <DSSubcategoryPage title="Authentication Configuration" posts={posts} />;
}
