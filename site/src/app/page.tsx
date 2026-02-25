import { SITE_TITLE, SITE_DESCRIPTION } from "@/lib/constants";

export default function Home() {
  return (
    <div className="flex flex-col md:flex-row gap-6">
      {/* Sidebar */}
      <aside className="hidden md:block md:w-1/4">
        <h3 className="text-center text-lg font-bold mb-4">{SITE_TITLE}</h3>
        <div className="well sidebar">
          <p className="italic text-sm">{SITE_DESCRIPTION}</p>
        </div>
        <div className="well sidebar">
          <h4 className="font-bold text-sm">A.D.D.? No, Polymath!</h4>
          <h5 className="text-sm mt-2">What&apos;s a polymath?</h5>
          <p className="text-sm mt-1">
            1. a person whose expertise fills a significant number of subject
            areas. From the Greek polymathēs, πολυμαθής, &quot;having learned
            much.&quot;
            <br />
            <span className="text-xs italic">Wikipedia</span>
          </p>
          <p className="text-sm mt-2">
            2. a highly functioning person with Attention Deficit Disorder
            (A.D.D.) who hangs around universities long enough to be awarded
            various degrees, ostensibly to entice the person to go away (unless,
            of course, they are good at bringing in grant money).
            <br />
            <span className="text-xs italic">Aaron D. Schroeder</span>
          </p>
        </div>
      </aside>

      {/* Main content */}
      <div className="w-full md:w-3/4">
        <div className="well">
          <div className="mb-6">
            <img
              className="float-left mr-6 mb-4"
              src="/images/Aaron_headshot_2019.jpg"
              alt="Aaron D. Schroeder"
              width={275}
            />
            <span className="name">
              <h3>Aaron D. Schroeder, Ph.D.</h3>
              <span className="font-bold">Research Associate Professor</span>
              <br />
              <a href="https://www.bi.vt.edu/sdal">
                Social &amp; Decision Analytics Division
              </a>
              ,{" "}
              <a href="https://www.bi.vt.edu/">
                University of Virginia Biocomplexity Institute &amp; Initiative
              </a>
              <br />
              <a href="mailto:aaron.schroeder@virginia.edu">
                aaron.schroeder@virginia.edu
              </a>
            </span>
          </div>

          <div className="clear-both" />

          <p className="biosketch">
            Dr. Schroeder&apos;s overarching research focus is the enablement of
            Evidence-Based Policy-Making and Program Evaluation through the
            Secure Liberation, Integration and Analysis of Administrative Data.
          </p>
          <p className="biosketch">
            Dr. Schroeder has extensive experience in the technologies and
            related policies of information/data integration and systems
            analysis, policy and program development and implementation,
            quantitative and qualitative methodologies of evaluation, and the
            general application of data and web technologies to the enhancement
            of public and private sector services.
          </p>
          <p className="biosketch">
            A particular focus of Dr. Schroeder&apos;s research has been on the
            integration and analysis of education, health, social service and
            non-profit administrative data streams for the purpose of conducting
            policy analyses and program evaluations impacting a wide range of
            constituents, including: pre-K child social and health service
            recipients; child care service operators; primary, secondary,
            post-secondary and adult education service recipients; state
            workforce training service recipients; and, U.S. veteran health and
            social service recipients.
          </p>
          <p className="biosketch">
            High-profile information integration projects in the Commonwealth of
            Virginia include the USED-funded Statewide Longitudinal Data System,
            the USHHS-funded Project Child HANDS, and the USDOT-funded design,
            development, deployment, and evaluation of the U.S.&apos;s first
            statewide travel information system, Virginia 511.
          </p>

          <h4 className="font-bold mt-6 mb-2">EDUCATION</h4>
          <table className="text-sm mb-4">
            <tbody>
              <tr><td className="font-bold pr-4">Virginia Tech University</td><td></td></tr>
              <tr><td className="pl-2 pr-4">Ph.D. in Public Policy &amp; Administration</td><td>2001</td></tr>
              <tr><td className="pl-2 pr-4 text-xs">Areas: Organization Theory, Data Management, Privacy Law, Implementation</td><td></td></tr>
              <tr><td className="pl-2 pr-4 text-xs">Dissertation: &quot;Building Implementation Networks&quot;</td><td></td></tr>
              <tr><td className="font-bold pr-4 pt-2">James Madison University</td><td></td></tr>
              <tr><td className="pl-2 pr-4">M.P.A. in Public Administration</td><td>1993</td></tr>
              <tr><td className="pl-2 pr-4 text-xs">Areas: Geographic Information Systems, Administrative Law</td><td></td></tr>
              <tr><td className="font-bold pr-4 pt-2">University of Delaware</td><td></td></tr>
              <tr><td className="pl-2 pr-4">B.A. in Psychology</td><td>1991</td></tr>
              <tr><td className="pl-2 pr-4 text-xs">Areas: Brain &amp; Behavior (incl. graduate-level Neuropsychology)</td><td></td></tr>
              <tr><td className="pl-2 pr-4 text-xs">Minor: Statistics</td><td></td></tr>
            </tbody>
          </table>

          <h4 className="font-bold mt-6 mb-2">SPECIALIZATIONS</h4>
          <div className="mb-3">
            <p className="font-bold text-sm">Policy &amp; Evaluation</p>
            <ul className="text-sm ml-4 list-disc">
              <li>Methods of Data Collection</li>
              <li>Research Design</li>
              <li>Quantitative &amp; Qualitative Data Analysis</li>
              <li>Information Policy</li>
              <li>Privacy Law</li>
              <li>Policy &amp; Implementation Network Analysis</li>
            </ul>
          </div>
          <div className="mb-3">
            <p className="font-bold text-sm">Information Management</p>
            <ul className="text-sm ml-4 list-disc">
              <li>Information Integration</li>
              <li>Data Management</li>
              <li>Big Data</li>
              <li>Web-Enabled Public Services</li>
            </ul>
          </div>
          <div className="mb-3">
            <p className="font-bold text-sm">
              Additional Specialized Training &amp; Technical Skills
            </p>
            <ul className="text-sm ml-4 list-disc">
              <li>Master R Developer</li>
              <li>Linux Server Administration</li>
              <li>Server Virtualization</li>
              <li>PostgreSQL Database Programming (PL/pgSQL)</li>
              <li>Oracle Database Programming (PL/SQL)</li>
              <li>Microsoft SQL Server Programming (T-SQL)</li>
              <li>JavaEE Multi-Tier Programming (Java, JPA, JSF, Facelets)</li>
              <li>Microsoft Server Administration</li>
              <li>ASP.NET Web Development (C#)</li>
              <li>Python Development</li>
              <li>Cisco Network Administration</li>
              <li>SAS &amp; SAS JMP</li>
              <li>SPSS</li>
              <li>Group Facilitation, Focus Groups, &amp; Nominal Groups</li>
              <li>Advanced Cold Fusion: Fusebox</li>
              <li>Advanced Graphics with Photoshop and GIMP</li>
            </ul>
          </div>

          <h4 className="font-bold mt-6 mb-2">HONORS, AWARDS, RECOGNITION</h4>
          <div className="text-sm space-y-3">
            <div>
              <p className="font-bold">Member, Arlington County Open Data Advisory Group, 2018-2019</p>
            </div>
            <div>
              <p className="font-bold">COVITS 2013 Winner, Cross-Boundary Collaboration on IT Initiatives</p>
              <p>(2013) Announced as the winner in the category of Cross-Boundary Collaboration on IT Initiatives for the Virginia Longitudinal Data System (VLDS).</p>
            </div>
            <div>
              <p className="font-bold">COVITS 2012 Finalist</p>
              <p>(2012) Announced as a Finalist for the Virginia Longitudinal Data System (VLDS).</p>
            </div>
            <div>
              <p className="font-bold">Virginia Early Childhood Advisory Council</p>
              <p>(2010) Invited to present to the Virginia Governor&apos;s Early Childhood Advisory Council (ECAC) on Project Child HANDS.</p>
            </div>
            <div>
              <p className="font-bold">National Institute of Statistical Sciences Workshop</p>
              <p>(2009) Invited to present on methods of public-sector data integration and issues created by federal and state privacy laws.</p>
            </div>
            <div>
              <p className="font-bold">National Press Club</p>
              <p>(2008) Invited to present findings on intergenerational day care facilities vs. traditional operations.</p>
            </div>
            <div>
              <p className="font-bold">Intelligent Transportation Systems Conference</p>
              <p>(2003) Invited speaker to the Florida DOT ITS Conference.</p>
            </div>
            <div>
              <p className="font-bold">Technology and Public Administration Conference</p>
              <p>(2000) Invited by University of LaVerne to lead two day workshop on stakeholder analysis and IT implementation in the public sector.</p>
            </div>
            <div>
              <p className="font-bold">Virginia Transportation Conference</p>
              <p>(1999 &amp; 2000) Invited to speak on public-private partnerships and IT deployment in rural areas.</p>
            </div>
            <div>
              <p className="font-bold">Association of State Governments</p>
              <p>(1999) Nominated for Award in Innovation in State Government for Travel Shenandoah.</p>
            </div>
            <div>
              <p className="font-bold">Member, Congressional Commission</p>
              <p>(1999) Appointed as a Member, Congressional Commission on I-81 Truck Safety.</p>
            </div>
            <div>
              <p className="font-bold">Eno Transportation Fellow</p>
              <p>(1997) Eno Transportation Fellow and graduate of Eno Transportation Foundation Leadership Development Program.</p>
            </div>
            <div>
              <p className="font-bold">Guest Editor</p>
              <p>(1997) Invited Guest Editor, Administration &amp; Society.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
