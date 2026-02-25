import DataScienceSidebar from "./DataScienceSidebar";

interface DataScienceLayoutProps {
  children: React.ReactNode;
}

export default function DataScienceLayout({ children }: DataScienceLayoutProps) {
  return (
    <div className="flex flex-col md:flex-row gap-6">
      <aside className="hidden md:block md:w-1/4">
        <DataScienceSidebar />
      </aside>
      <div className="w-full md:w-3/4">{children}</div>
    </div>
  );
}
