const SKILLS = [
  "R",
  "Python",
  "PostgreSQL",
  "Oracle PL/SQL",
  "MS SQL Server",
  "Linux Admin",
  "Docker",
  "JavaEE",
  "ASP.NET/C#",
  "SAS",
  "SPSS",
  "Network Admin",
  "Photoshop/GIMP",
  "LLMs/AI",
];

const HONORS: { year: string; label: string }[] = [
  { year: "2018–2019", label: "Member, Arlington County Open Data Advisory Group" },
  { year: "2013", label: "COVITS Winner — Cross-Boundary Collaboration on IT (VLDS)" },
  { year: "2012", label: "COVITS Finalist — Virginia Longitudinal Data System" },
  { year: "2010", label: "Invited, Virginia Governor's Early Childhood Advisory Council" },
  { year: "2009", label: "Invited, National Institute of Statistical Sciences Workshop" },
  { year: "2008", label: "Invited, National Press Club — intergenerational day care findings" },
  { year: "2003", label: "Invited speaker, Florida DOT ITS Conference" },
  { year: "2000", label: "Invited workshop lead, Univ. of LaVerne — IT implementation" },
  { year: "1999–2000", label: "Invited, Virginia Transportation Conference" },
  { year: "1999", label: "Nominee, ASG Award for Innovation in State Government (Travel Shenandoah)" },
  { year: "1999", label: "Appointed Member, Congressional Commission on I-81 Truck Safety" },
  { year: "1997", label: "Eno Transportation Fellow" },
  { year: "1997", label: "Invited Guest Editor, Administration & Society" },
];

export default function Home() {
  return (
    <div className="space-y-10">
      {/* ─── Hero ───────────────────────────────────────────── */}
      <section className="flex flex-col md:flex-row gap-8 items-start">
        <img
          src="/images/Aaron_headshot_2019.jpg"
          alt="Aaron D. Schroeder"
          width={240}
          height={300}
          className="rounded-md shadow-md w-full max-w-[240px] md:w-60"
          style={{ border: "1px solid var(--border)" }}
        />
        <div className="flex-1">
          <p className="section-label">Bio</p>
          <h1
            style={{
              fontFamily: "var(--font-display)",
              color: "var(--accent)",
              fontSize: "clamp(2rem, 5vw, 3rem)",
              lineHeight: 1.05,
              fontWeight: 400,
              marginBottom: "0.5rem",
            }}
          >
            Aaron D. Schroeder, Ph.D.
          </h1>
          <p
            className="text-lg"
            style={{ color: "var(--text-muted)", lineHeight: 1.5 }}
          >
            Research Associate Professor,{" "}
            <a href="https://www.bi.vt.edu/sdal">Social &amp; Decision Analytics Division</a>
            ,{" "}
            <a href="https://www.bi.vt.edu/">University of Virginia Biocomplexity Institute</a>
          </p>
          <p className="mt-3">
            <a href="mailto:aaron.schroeder@virginia.edu">
              aaron.schroeder@virginia.edu
            </a>
          </p>
        </div>
      </section>

      {/* ─── Research Focus ─────────────────────────────────── */}
      <section>
        <p className="section-label">Research Focus</p>
        <div className="panel p-6 space-y-3">
          <p className="biosketch">
            Dr. Schroeder&apos;s overarching research focus is the enablement of{" "}
            <strong>Evidence-Based Policy-Making</strong> and{" "}
            <strong>Program Evaluation</strong> through the secure liberation,
            integration and analysis of administrative data.
          </p>
          <p className="biosketch">
            A particular focus has been the integration of education, health,
            social service and non-profit administrative data streams to support
            policy analyses and program evaluations across pre-K services, child
            care, K-12 and adult education, state workforce training, and U.S.
            veteran services.
          </p>
          <p className="biosketch">
            High-profile information integration projects in the Commonwealth of
            Virginia include the USED-funded{" "}
            <strong>Statewide Longitudinal Data System</strong>, the USHHS-funded{" "}
            <strong>Project Child HANDS</strong>, and the USDOT-funded design and
            evaluation of the U.S.&apos;s first statewide travel information
            system, <strong>Virginia 511</strong>.
          </p>
        </div>
      </section>

      {/* ─── Education + Specializations grid ───────────────── */}
      <section className="grid md:grid-cols-2 gap-8">
        {/* Education */}
        <div>
          <p className="section-label">Education</p>
          <div className="panel divide-y" style={{ borderColor: "var(--border)" }}>
            <div className="p-5">
              <p className="font-semibold" style={{ color: "var(--accent)" }}>
                Virginia Tech University
              </p>
              <p className="text-sm mt-1">
                Ph.D., Public Policy &amp; Administration · 2001
              </p>
              <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                Organization Theory · Data Management · Privacy Law · Implementation
                <br />
                Dissertation: &ldquo;Building Implementation Networks&rdquo;
              </p>
            </div>
            <div className="p-5">
              <p className="font-semibold" style={{ color: "var(--accent)" }}>
                James Madison University
              </p>
              <p className="text-sm mt-1">
                M.P.A., Public Administration · 1993
              </p>
              <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                Geographic Information Systems · Administrative Law
              </p>
            </div>
            <div className="p-5">
              <p className="font-semibold" style={{ color: "var(--accent)" }}>
                University of Delaware
              </p>
              <p className="text-sm mt-1">B.A., Psychology · 1991</p>
              <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                Brain &amp; Behavior (incl. graduate-level Neuropsychology) · Minor in Political Science
              </p>
            </div>
          </div>
        </div>

        {/* Specializations */}
        <div>
          <p className="section-label">Specializations</p>
          <div className="panel p-5 space-y-4">
            <div>
              <p
                className="text-sm font-semibold mb-2"
                style={{ color: "var(--accent)" }}
              >
                Policy &amp; Evaluation
              </p>
              <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                Methods of data collection · research design · quantitative
                &amp; qualitative analysis · information policy · privacy law ·
                policy/implementation network analysis
              </p>
            </div>
            <div>
              <p
                className="text-sm font-semibold mb-2"
                style={{ color: "var(--accent)" }}
              >
                Information Management
              </p>
              <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                Information integration · data management · big data ·
                web-enabled public services
              </p>
            </div>
            <div>
              <p
                className="text-sm font-semibold mb-2"
                style={{ color: "var(--accent)" }}
              >
                Technical Skills
              </p>
              <div className="flex flex-wrap gap-1.5">
                {SKILLS.map((s) => (
                  <span key={s} className="chip">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Honors ─────────────────────────────────────────── */}
      <section>
        <p className="section-label">Honors, Awards, Recognition</p>
        <ul
          className="panel divide-y text-sm"
          style={{ borderColor: "var(--border)" }}
        >
          {HONORS.map((h, i) => (
            <li
              key={i}
              className="flex items-start justify-between gap-4 px-5 py-3"
            >
              <span>{h.label}</span>
              <span
                className="shrink-0 font-mono text-xs"
                style={{ color: "var(--gold)" }}
              >
                {h.year}
              </span>
            </li>
          ))}
        </ul>
      </section>

      {/* ─── Polymath callout ───────────────────────────────── */}
      <section
        className="border-l-4 pl-6 py-2"
        style={{ borderColor: "var(--gold)" }}
      >
        <p className="section-label">A.D.D.? No, Polymath!</p>
        <div className="grid md:grid-cols-2 gap-6 text-sm">
          <div>
            <p className="font-semibold mb-1" style={{ color: "var(--accent)" }}>
              Wikipedia
            </p>
            <p style={{ color: "var(--text-muted)" }}>
              A person whose expertise spans a significant number of subject
              areas. From the Greek <em>polymathēs</em> (πολυμαθής), &ldquo;having
              learned much.&rdquo;
            </p>
          </div>
          <div>
            <p className="font-semibold mb-1" style={{ color: "var(--accent)" }}>
              Aaron D. Schroeder
            </p>
            <p style={{ color: "var(--text-muted)" }}>
              A highly functioning person with A.D.D. who hangs around
              universities long enough to be awarded various degrees, ostensibly
              to entice the person to go away (unless, of course, they are good
              at bringing in grant money).
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
