import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getPostsByCategory, sortByOrdinal } from "@/lib/content";

export default async function EncryptedStoragePage() {
  const posts = sortByOrdinal(getPostsByCategory("encryptedstorage"));
  return <DSSubcategoryPage title="Encrypted Storage" posts={posts} />;
}
