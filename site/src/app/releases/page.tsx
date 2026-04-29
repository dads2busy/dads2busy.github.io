import CategoryLayout from "@/components/CategoryLayout";
import ReleasePost from "@/components/ReleasePost";
import { getPostsByCategory } from "@/lib/content";
import { ReleasePost as ReleasePostType } from "@/lib/types";

export default function ReleasesPage() {
  const posts = getPostsByCategory("release") as ReleasePostType[];
  posts.sort((a, b) => (b.date || "").localeCompare(a.date || ""));

  return (
    <CategoryLayout category="release">
      {posts.map((post) => (
        <ReleasePost key={post.slug} post={post} />
      ))}
    </CategoryLayout>
  );
}
