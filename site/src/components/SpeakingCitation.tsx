import { SpeakingPost } from "@/lib/types";
import { renderMarkdown, truncateContent } from "@/lib/content";

interface Props {
  post: SpeakingPost;
}

export default async function SpeakingCitation({ post }: Props) {
  const htmlContent = await renderMarkdown(post.abstract);
  const year = post.date ? post.date.slice(0, 4) : "";
  const media = [
    { link: post.media1, title: post.media1title },
    { link: post.media2, title: post.media2title },
    { link: post.media3, title: post.media3title },
  ].filter((m) => m.link && m.link.trim() !== "");

  return (
    <div className="mb-6">
      <p className="font-semibold text-sm mb-1">
        {post.title}{year && <> ({year})</>}
      </p>
      <p className="text-sm">
        {htmlContent ? truncateContent(htmlContent, 100) : ""}
      </p>
      <table className="text-sm mt-1">
        <tbody>
          {post.role && (
            <tr>
              <td className="pr-4 font-semibold align-top">Role:</td>
              <td>{post.role}</td>
            </tr>
          )}
          {post.sponsor && post.sponsor.trim() !== "" && (
            <tr>
              <td className="pr-4 font-semibold align-top">Sponsor:</td>
              <td>{post.sponsor}</td>
            </tr>
          )}
          {post.dates && (
            <tr>
              <td className="pr-4 font-semibold align-top">Dates:</td>
              <td>{post.dates}</td>
            </tr>
          )}
        </tbody>
      </table>
      {post.report && post.report.trim() !== "" && (
        <p className="text-sm mt-1">
          <a href={`/downloads/${post.report}`}>Presentation: {post.report}</a>
        </p>
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
