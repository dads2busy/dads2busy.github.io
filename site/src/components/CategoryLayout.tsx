import Sidebar from "./Sidebar";

interface CategoryLayoutProps {
  category: string;
  children: React.ReactNode;
}

export default function CategoryLayout({ category, children }: CategoryLayoutProps) {
  return (
    <div className="flex flex-col md:flex-row gap-6">
      <aside className="hidden md:block md:w-1/4">
        <Sidebar category={category} />
      </aside>
      <div className="w-full md:w-3/4">{children}</div>
    </div>
  );
}
