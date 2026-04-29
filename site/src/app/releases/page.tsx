import CategoryLayout from "@/components/CategoryLayout";
import ReleasePost from "@/components/ReleasePost";
import { getPostsByCategory } from "@/lib/content";
import { ReleasePost as ReleasePostType } from "@/lib/types";

export default function ReleasesPage() {
  const posts = getPostsByCategory("release") as ReleasePostType[];
  posts.sort((a, b) => (b.date || "").localeCompare(a.date || ""));

  return (
    <CategoryLayout category="release">
      <h3 className="text-lg font-bold border-b border-black pb-1 mb-4 mt-6">
        Software and Datasets
      </h3>
      {posts.map((post) => (
        <ReleasePost key={post.slug} post={post} />
      ))}
    </CategoryLayout>
  );
}
