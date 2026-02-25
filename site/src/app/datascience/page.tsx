import DataScienceLayout from "@/components/DataScienceLayout";

export default function DataSciencePage() {
  return (
    <DataScienceLayout>
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">SDAL Data Science Framework</h2>
        <h3 className="text-lg font-bold mb-4">Generalized Framework</h3>
        <p className="text-sm mb-4 max-w-2xl mx-auto">
          Much of this is discussed in: Keller, S. A., Shipp, S. S., Schroeder,
          A. D., &amp; Korkmaz, G. (2020). Doing Data Science: A Framework and
          Case Study. Harvard Data Science Review. 2(1).
          DOI=https://doi.org/10.1162/99608f92.2d83f7f5.
        </p>
        <img
          src="/images/data-science-framework-overview.png"
          width={450}
          alt="Data Science Framework Overview"
          className="inline-block mb-4"
        />
        <img
          src="/images/CLD3_iteration.png"
          width={350}
          alt="CLD3 Iteration"
          className="inline-block mb-4"
        />
        <h3 className="text-lg font-bold mt-4 mb-4">Processes &amp; Platforms</h3>
        <img
          src="/images/data-science-processes-platforms.png"
          width={675}
          alt="Data Science Processes and Platforms"
          className="inline-block"
        />
      </div>
    </DataScienceLayout>
  );
}
