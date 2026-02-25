import DSSubcategoryPage from "@/components/DSSubcategoryPage";
import { getAllPosts, sortByOrdinal } from "@/lib/content";

const LANGUAGES: Record<string, string> = {
  R: "R Code Examples",
  bash: "Bash Code Examples",
  SQL: "SQL Code Examples",
  MANN: "MANN Tool",
};

export function generateStaticParams() {
  return Object.keys(LANGUAGES).map((language) => ({ language }));
}

export default async function LanguagePage({
  params,
}: {
  params: Promise<{ language: string }>;
}) {
  const { language } = await params;
  const title = LANGUAGES[language] || language;

  const posts = sortByOrdinal(
    getAllPosts().filter(
      (p) => p.category?.toLowerCase() === language.toLowerCase()
    )
  );

  return <DSSubcategoryPage title={title} posts={posts} />;
}
