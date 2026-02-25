import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getPostsByCategory, sortByOrdinal } from "@/lib/content";

export default async function PermissionsConfigPage() {
  const posts = sortByOrdinal(getPostsByCategory("permissionsconfig"));
  return <DSSubcategoryPage title="Permissions Configuration" posts={posts} />;
}
