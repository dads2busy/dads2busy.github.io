import { ResearchPost as ResearchPostType } from "@/lib/types";

interface Props {
  post: ResearchPostType;
}

export default function ResearchPost({ post }: Props) {
  const reports = [post.report, post.report2, post.report3, post.report4, post.report5, post.report6].filter(
    (r) => r && r.trim() !== ""
  );
  const media = [
    { link: post.media1, title: post.media1title },
    { link: post.media2, title: post.media2title },
    { link: post.media3, title: post.media3title },
  ].filter((m) => m.link && m.link.trim() !== "");

  return (
    <div className="mb-6">
      <h4 className="font-bold">{post.title}</h4>
      <table className="text-sm mt-1">
        <tbody>
          {post.award && (
            <tr>
              <td className="pr-4 font-semibold align-top">Award:</td>
              <td>{post.award}</td>
            </tr>
          )}
          {post.role && (
            <tr>
              <td className="pr-4 font-semibold align-top">Role:</td>
              <td>{post.role}</td>
            </tr>
          )}
          {post.funder && (
            <tr>
              <td className="pr-4 font-semibold align-top">Funder:</td>
              <td>{post.funder}</td>
            </tr>
          )}
          {post.dates && (
            <tr>
              <td className="pr-4 font-semibold align-top">Dates:</td>
              <td>{post.dates}</td>
            </tr>
          )}
          {post.abstract && post.abstract.trim() !== "" && (
            <tr>
              <td className="pr-4 font-semibold align-top">Abstract:</td>
              <td>{post.abstract}</td>
            </tr>
          )}
        </tbody>
      </table>
      {post.website && post.website.trim() !== "" && (
        <p className="text-sm mt-1">
          <a href={post.website} target="_blank" rel="noopener noreferrer">
            Project Website
          </a>
        </p>
      )}
      {reports.length > 0 && (
        <div className="text-sm mt-1">
          {reports.map((r, i) => (
            <p key={i}>
              <a href={`/downloads/${r}`}>Report: {r}</a>
            </p>
          ))}
        </div>
      )}
      {media.length > 0 && (
        <div className="text-sm mt-1">
          {media.map((m, i) => (
            <p key={i}>
              <a href={m.link!}>{m.title || "Media"}</a>
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
