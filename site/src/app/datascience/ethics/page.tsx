import DataScienceLayout from "@/components/DataScienceLayout";

export default function EthicsPage() {
  return (
    <DataScienceLayout>
      <h2 className="text-xl font-bold mb-6 text-center">
        Ethics Checklist Template for Data Science Projects
      </h2>

      <div className="space-y-6 text-sm">
        <table className="w-full border-collapse border border-gray-300">
          <thead><tr><th className="border border-gray-300 p-2 bg-gray-100 text-left">Project Initiation</th></tr></thead>
          <tbody>
            <tr><td className="border border-gray-300 p-2 italic">Recognize and affirm that all project plans will incorporate regular checks, discussion, and documentation to ensure adherence to the ethical principles of research.</td></tr>
          </tbody>
        </table>

        <table className="w-full border-collapse border border-gray-300">
          <thead><tr><th className="border border-gray-300 p-2 bg-gray-100 text-left">Problem Identification (Relevant Theories and Working Hypotheses)</th></tr></thead>
          <tbody>
            <tr><td className="border border-gray-300 p-2 italic">Establish the ethical basis for undertaking the project as well as the project requirements of both the protection of research participant and the equitable allocation of all potential project benefits and risks.</td></tr>
            <tr><td className="border border-gray-300 p-2">
              <ol className="list-decimal ml-6 space-y-1">
                <li>What are the expected benefits of the project to the &quot;public good,&quot; and do they outweigh potential risks to participant welfare?</li>
                <li>Are there implicit assumptions and biases in the framing of the project regarding the studied communities and how will they be addressed?</li>
                <li>What type of Institutional Review Board (IRB) approval process is needed? Has the team reviewed the IRB protocol?</li>
              </ol>
            </td></tr>
          </tbody>
        </table>

        <table className="w-full border-collapse border border-gray-300">
          <thead><tr><th className="border border-gray-300 p-2 bg-gray-100 text-left">Data Discovery, Inventory, Screening, &amp; Acquisition</th></tr></thead>
          <tbody>
            <tr><td className="border border-gray-300 p-2 italic">Consider potential biases that may be introduced through the choice of datasets and variables.</td></tr>
            <tr><td className="border border-gray-300 p-2">
              <ol className="list-decimal ml-6 space-y-1" start={4}>
                <li>Do the data include disproportionate coverage of the different communities of study?</li>
                <li>Do data have adequate geographic coverage?</li>
                <li>Have checks and balances been established to identify and address implicit biases in the data?</li>
              </ol>
            </td></tr>
          </tbody>
        </table>

        <table className="w-full border-collapse border border-gray-300">
          <thead><tr><th className="border border-gray-300 p-2 bg-gray-100 text-left">Data Ingestion and Governance</th></tr></thead>
          <tbody>
            <tr><td className="border border-gray-300 p-2 italic">Put in place data platforms and processes to ensure data transfer, storage, and database development adheres to data governance agreements and best practices for data quality assurance.</td></tr>
            <tr><td className="border border-gray-300 p-2">
              <ol className="list-decimal ml-6 space-y-1" start={7}>
                <li>Have team members reviewed standard operating procedures (SOPs) and data management plans?</li>
                <li>Do data have adequate geographic coverage?</li>
                <li>Do additional procedures need to be defined for this project?</li>
              </ol>
            </td></tr>
          </tbody>
        </table>

        <table className="w-full border-collapse border border-gray-300">
          <thead><tr><th className="border border-gray-300 p-2 bg-gray-100 text-left">Statistical Modeling &amp; Analysis</th></tr></thead>
          <tbody>
            <tr><td className="border border-gray-300 p-2 italic">Establish transparency in methods, results and limitations.</td></tr>
            <tr><td className="border border-gray-300 p-2">
              <ol className="list-decimal ml-6 space-y-1" start={10}>
                <li>Have project methods and outputs been made as transparent as possible?</li>
                <li>Are the potential limitations of the research clearly presented?</li>
                <li>Should the research be used as the basis for policy action, have the predicted benefits and social costs to all potentially affected communities been considered?</li>
              </ol>
            </td></tr>
          </tbody>
        </table>

        <table className="w-full border-collapse border border-gray-300">
          <thead><tr><th className="border border-gray-300 p-2 bg-gray-100 text-left">Fitness-for-Use Assessment</th></tr></thead>
          <tbody>
            <tr><td className="border border-gray-300 p-2 italic">Critically assess the overall utility of the results in achieving the predicted benefits of the study, to be transparent about potential limitations of the study, and to ensure that unintended biases haven&apos;t been introduced as a result of data choice and model refinement.</td></tr>
            <tr><td className="border border-gray-300 p-2">
              <ol className="list-decimal ml-6 space-y-1" start={13}>
                <li>What are the limitations of the results? Are the results useful given the purpose of the study?</li>
                <li>Do the statistical results support the potential benefits of the study previously stated?</li>
                <li>Do the statistical results support the mitigation of the potential risks of the study previously stated?</li>
                <li>Have any data been deemed unusable that require revisiting the question of potential biases?</li>
              </ol>
            </td></tr>
          </tbody>
        </table>

        <table className="w-full border-collapse border border-gray-300">
          <thead><tr><th className="border border-gray-300 p-2 bg-gray-100 text-left">Communication and Dissemination</th></tr></thead>
          <tbody>
            <tr><td className="border border-gray-300 p-2 italic">Summarize questions and actions taken to reinforce the process of ethical consideration on all continuing and future projects. Establish protocols for replication and expansion of the research findings, and information dissemination.</td></tr>
            <tr><td className="border border-gray-300 p-2">
              <ol className="list-decimal ml-6 space-y-1" start={17}>
                <li>Did key ethical questions arise during the research and, if so, how were they addressed?</li>
                <li>Are research protocols, methods and data available to other researchers?</li>
              </ol>
            </td></tr>
          </tbody>
        </table>
      </div>
    </DataScienceLayout>
  );
}
