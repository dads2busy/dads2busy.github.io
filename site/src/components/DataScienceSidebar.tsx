"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface AccordionSection {
  title: string;
  content: React.ReactNode;
}

const sections: AccordionSection[] = [
  {
    title: "Data Science Framework",
    content: (
      <div>
        <ul className="list-none pl-0 mb-3 text-sm">
          <li className="mt-1"><Link href="/datascience">Data Science Framework & Processes</Link></li>
          <li className="mt-1"><Link href="/datascience/ethics">Ethics Checklist</Link></li>
        </ul>
        <h4 className="font-bold text-sm mt-3 mb-1">Data Discovery</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1"><Link href="/datadiscovery/identification">Identification</Link></li>
          <li className="mt-1"><Link href="/datadiscovery/screening">Screening</Link></li>
          <li className="mt-1"><Link href="/datadiscovery/inventory">Inventory</Link></li>
          <li className="mt-1"><Link href="/datadiscovery/access">Data Access</Link></li>
        </ul>
        <h4 className="font-bold text-sm mt-3 mb-1">Data Profiling</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1"><Link href="/dataprofiling/dataquality">Quality</Link></li>
          <li className="mt-1"><Link href="/dataprofiling/datastructure">Structure</Link></li>
          <li className="mt-1"><Link href="/dataprofiling/metadata">Metadata</Link></li>
        </ul>
        <h4 className="font-bold text-sm mt-3 mb-1">Data Preparation</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1"><Link href="/datapreparation/datacleaning">Cleaning</Link></li>
          <li className="mt-1"><Link href="/datapreparation/datatransformation">Transformation</Link></li>
          <li className="mt-1"><Link href="/datapreparation/datarestructuring">Restructuring</Link></li>
          <li className="mt-1"><Link href="/datapreparation/datacreation">Creating</Link></li>
        </ul>
        <h4 className="font-bold text-sm mt-3 mb-1">Data Linkage</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1">Ontology Alignment</li>
          <li className="mt-1"><Link href="/datalinkage/recordlinkage">Entity Resolution</Link></li>
        </ul>
        <h4 className="font-bold text-sm mt-3 mb-1">Data Exploration</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1"><Link href="/dataexploration/characterization">Characterization</Link></li>
          <li className="mt-1">Visualization</li>
        </ul>
        <h4 className="font-bold text-sm mt-3 mb-1">Data Analysis</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1">Inference</li>
          <li className="mt-1">Textual Analysis</li>
          <li className="mt-1">Network Analysis</li>
          <li className="mt-1">Agent Modeling</li>
          <li className="mt-1">Machine Learning</li>
        </ul>
        <h4 className="font-bold text-sm mt-3 mb-1">Data Fitness</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1"><Link href="/datafitness/fitnessforuse">Fitness for Use</Link></li>
        </ul>
      </div>
    ),
  },
  {
    title: "Data Science Platform",
    content: (
      <div>
        <h4 className="font-bold text-sm mb-1">Server Configuration</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1"><Link href="/encryptedstorage">Encrypted Storage</Link></li>
          <li className="mt-1"><Link href="/lxcconfig">LXC Container Configuration</Link></li>
          <li className="mt-1"><Link href="/authconfig">Authentication Configuration</Link></li>
          <li className="mt-1"><Link href="/permissionsconfig">Permissions Configuration</Link></li>
          <li className="mt-1">Software Configuration
            <ul className="list-none pl-3 text-xs">
              <li className="mt-1">Apache Spark</li>
              <li className="mt-1">RStudio Server</li>
              <li className="mt-1">Shiny Server</li>
              <li className="mt-1">Jupyter Server</li>
              <li className="mt-1">PostgreSQL</li>
            </ul>
          </li>
        </ul>
        <h4 className="font-bold text-sm mt-3 mb-1">Workstation Configuration</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1"><Link href="/macsetup">Mac</Link></li>
          <li className="mt-1">Linux</li>
          <li className="mt-1">Windows</li>
        </ul>
      </div>
    ),
  },
  {
    title: "Code Examples & Tools",
    content: (
      <div>
        <h4 className="font-bold text-sm mb-1">Code Examples</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1"><Link href="/languages/R">R</Link></li>
          <li className="mt-1">Python</li>
          <li className="mt-1"><Link href="/languages/bash">Bash</Link></li>
          <li className="mt-1"><Link href="/languages/SQL">SQL</Link></li>
        </ul>
        <h4 className="font-bold text-sm mt-3 mb-1">Tools</h4>
        <ul className="list-none pl-2 text-sm">
          <li className="mt-1">d3</li>
          <li className="mt-1">iGraph</li>
          <li className="mt-1">GATE</li>
          <li className="mt-1"><Link href="/languages/MANN">MANN</Link></li>
          <li className="mt-1">SAFR-Link</li>
          <li className="mt-1">Protege</li>
        </ul>
      </div>
    ),
  },
  {
    title: "Data Management",
    content: (
      <ul className="list-none pl-0 text-sm">
        <li className="mt-1"><Link href="/datamanagement/datamanagementplan">Data Management Plan</Link></li>
      </ul>
    ),
  },
  {
    title: "Project Management",
    content: (
      <ul className="list-none pl-0 text-sm">
        <li className="mt-1">Project File Layout</li>
      </ul>
    ),
  },
];

export default function DataScienceSidebar() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("ds-accordion-index");
    if (saved !== null) {
      setOpenIndex(parseInt(saved, 10));
    } else {
      setOpenIndex(0);
    }
  }, []);

  const toggle = (index: number) => {
    const newIndex = openIndex === index ? null : index;
    setOpenIndex(newIndex);
    if (newIndex !== null) {
      localStorage.setItem("ds-accordion-index", String(newIndex));
    } else {
      localStorage.removeItem("ds-accordion-index");
    }
  };

  return (
    <div className="text-sm">
      {sections.map((section, i) => (
        <div key={section.title} className="border border-gray-300 mb-[-1px]">
          <button
            onClick={() => toggle(i)}
            className="w-full text-left px-3 py-2 bg-gray-100 hover:bg-gray-200 font-bold text-sm flex justify-between items-center"
          >
            {section.title}
            <span className="text-xs">{openIndex === i ? "▼" : "▶"}</span>
          </button>
          {openIndex === i && (
            <div className="px-3 py-2 border-t border-gray-200">
              {section.content}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
