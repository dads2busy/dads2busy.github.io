import { SITE_TITLE, SITE_DESCRIPTION } from "@/lib/constants";
import LinksList from "./LinksList";

interface SidebarProps {
  category: string;
}

export default function Sidebar({ category }: SidebarProps) {
  return (
    <div>
      <h3 className="text-center text-lg font-bold mb-4">{SITE_TITLE}</h3>
      <div className="well sidebar">
        <p className="italic text-sm">{SITE_DESCRIPTION}</p>
      </div>
      <div className="well sidebar">
        <LinksList category={category} />
      </div>
    </div>
  );
}
