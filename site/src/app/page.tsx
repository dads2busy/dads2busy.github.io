import fs from "fs";
import path from "path";
import yaml from "js-yaml";
import { siteExtrasSchema } from "@/lib/site-extras-schema";

type ProfileEducationEntry = {
  institution: string;
  area?: string;
  degree?: string;
  date?: string;
  highlights?: string[];
};

type ProfileAward = { label: string; details?: string };

type ProfileSpecialization = { label: string; details: string };

type Profile = {
  cv: {
    name: string;
    email: string;
    sections: {
      Summary: string[];
      Education: ProfileEducationEntry[];
      Skills: string[];
      Specializations: ProfileSpecialization[];
      "Awards & Honors": ProfileAward[];
    };
  };
};

const profile = yaml.load(
  fs.readFileSync(path.join(process.cwd(), "content", "profile.yaml"), "utf8"),
) as Profile;

const extras = siteExtrasSchema.parse(
  yaml.load(
    fs.readFileSync(path.join(process.cwd(), "content", "site_extras.yaml"), "utf8"),
  ),
);

const summaryParagraphs = profile.cv.sections.Summary;
const educationEntries = profile.cv.sections.Education;
const awards = profile.cv.sections["Awards & Honors"];
const skills = profile.cv.sections.Skills;
const specializations = profile.cv.sections.Specializations as Array<{ label: string; details: string }>;

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
          {summaryParagraphs.map((p, i) => (
            <p key={i} className="biosketch">{p}</p>
          ))}
        </div>
      </section>

      {/* ─── Education + Specializations grid ───────────────── */}
      <section className="grid md:grid-cols-2 gap-8">
        {/* Education */}
        <div>
          <p className="section-label">Education</p>
          <div className="panel divide-y" style={{ borderColor: "var(--border)" }}>
            {educationEntries.map((edu, i) => (
              <div key={i} className="p-5">
                <p className="font-semibold" style={{ color: "var(--accent)" }}>
                  {edu.institution}
                </p>
                {(edu.degree || edu.area || edu.date) && (
                  <p className="text-sm mt-1">
                    {edu.degree}{edu.degree && edu.area ? ", " : ""}{edu.area}
                    {edu.date ? ` · ${edu.date}` : ""}
                  </p>
                )}
                {edu.highlights && edu.highlights.length > 0 && (
                  <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                    {edu.highlights.join(" · ")}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Specializations */}
        <div>
          <p className="section-label">Specializations</p>
          <div className="panel p-5 space-y-4">
            {specializations.map((spec, i) => (
              <div key={i}>
                <p className="text-sm font-semibold mb-2" style={{ color: "var(--accent)" }}>
                  {spec.label}
                </p>
                <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                  {spec.details}
                </p>
              </div>
            ))}
            <div>
              <p className="text-sm font-semibold mb-2" style={{ color: "var(--accent)" }}>
                Technical Skills
              </p>
              <div className="flex flex-wrap gap-1.5">
                {skills.map((s) => (
                  <span key={s} className="chip">{s}</span>
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
          {awards.map((a, i) => (
            <li
              key={i}
              className="flex items-start justify-between gap-4 px-5 py-3"
            >
              <span>{a.label}</span>
              <span
                className="shrink-0 font-mono text-xs"
                style={{ color: "var(--gold)" }}
              >
                {a.details}
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
              {extras.polymath_callout.wikipedia_def}
            </p>
          </div>
          <div>
            <p className="font-semibold mb-1" style={{ color: "var(--accent)" }}>
              Aaron D. Schroeder
            </p>
            <p style={{ color: "var(--text-muted)" }}>
              {extras.polymath_callout.schroeder_def}
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
