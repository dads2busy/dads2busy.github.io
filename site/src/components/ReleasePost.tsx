import { ReleasePost as ReleasePostType } from "@/lib/types";

interface Props {
  post: ReleasePostType;
}

export default function ReleasePost({ post }: Props) {
  return (
    <div className="mb-6">
      <h4 className="font-bold">{post.title}</h4>
      <table className="text-sm mt-1">
        <tbody>
          {post.subcategory && (
            <tr>
              <td className="pr-4 font-semibold align-top">Type:</td>
              <td>{post.subcategory}</td>
            </tr>
          )}
          {post.date && (
            <tr>
              <td className="pr-4 font-semibold align-top">Date:</td>
              <td>{post.date.slice(0, 10)}</td>
            </tr>
          )}
          {post.summary && (
            <tr>
              <td className="pr-4 font-semibold align-top">Summary:</td>
              <td>{post.summary}</td>
            </tr>
          )}
          {post.url && (
            <tr>
              <td className="pr-4 font-semibold align-top">Link:</td>
              <td>
                <a href={post.url} target="_blank" rel="noopener noreferrer">
                  {post.url}
                </a>
              </td>
            </tr>
          )}
          {post.doi && (
            <tr>
              <td className="pr-4 font-semibold align-top">DOI:</td>
              <td>
                <a
                  href={`https://doi.org/${post.doi.replace(/^https?:\/\/(?:dx\.)?doi\.org\//, "")}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {post.doi}
                </a>
              </td>
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
    </div>
  );
}
