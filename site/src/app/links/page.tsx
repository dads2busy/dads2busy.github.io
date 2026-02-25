import LinksList from "@/components/LinksList";

export default function LinksPage() {
  return (
    <div className="well">
      <h2 className="text-xl font-bold mb-4">Links</h2>
      <LinksList category="default" />
    </div>
  );
}
