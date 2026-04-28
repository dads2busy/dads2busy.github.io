interface LinksListProps {
  category: string;
}

export default function LinksList({ category }: LinksListProps) {
  switch (category) {
    case "writing":
      return (
        <ul className="list-none p-0 text-sm">
          <li className="mt-2">
            <a href="/2020/03/harvard_econ">Featured: Integrating Data</a>
          </li>
          <li className="mt-2">
            <a href="/2020/03/hdsr">Featured: Data Science Framework</a>
          </li>
        </ul>
      );
    case "teaching":
      return (
        <div className="text-center">
          <img
            src="/images/lecture_icon.png"
            alt="Teaching"
            className="mx-auto max-w-full"
          />
        </div>
      );
    case "research":
      return (
        <div className="text-center">
          <img
            src="/images/data-researcher.png"
            alt="Research"
            className="mx-auto max-w-full"
          />
        </div>
      );
    case "speaking":
      return (
        <div className="text-center">
          <img
            src="/images/lecture_icon.png"
            alt="Speaking"
            className="mx-auto max-w-full"
          />
        </div>
      );
    case "coaching":
      return (
        <ul className="list-none p-0 text-sm">
          <li className="mt-2">
            <a href="https://www.littleleague.org">Little League</a>
          </li>
          <li className="mt-2">
            <a href="https://www.usyouthsoccer.org">US Youth Soccer</a>
          </li>
          <li className="mt-2">
            <a href="https://www.usaswimming.org">USA Swimming</a>
          </li>
        </ul>
      );
    case "working":
      return (
        <table className="text-xs">
          <tbody>
            <tr>
              <td>Tumble outta bed</td>
            </tr>
            <tr>
              <td>And stumble to the kitchen</td>
            </tr>
            <tr>
              <td>Pour myself a cup of ambition</td>
            </tr>
            <tr>
              <td>And yawn and stretch</td>
            </tr>
            <tr>
              <td>And try to come to life</td>
            </tr>
            <tr>
              <td className="pt-2 italic">- Dolly Parton, 9 to 5</td>
            </tr>
          </tbody>
        </table>
      );
    default:
      return (
        <ul className="list-none p-0 text-sm">
          <li className="mt-2">
            <a href="https://www.bi.vt.edu">Biocomplexity Institute</a>
          </li>
          <li className="mt-2">
            <a href="https://www.bi.vt.edu/sdal">Social & Decision Analytics</a>
          </li>
        </ul>
      );
  }
}
