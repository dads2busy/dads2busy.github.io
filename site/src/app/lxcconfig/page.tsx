import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getPostsByCategory, sortByOrdinal } from "@/lib/content";

export default async function LxcConfigPage() {
  const posts = sortByOrdinal(getPostsByCategory("lxcconfig"));
  return <DSSubcategoryPage title="LXC Container Configuration" posts={posts} />;
}
