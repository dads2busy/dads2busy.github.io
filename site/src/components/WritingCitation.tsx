import Link from "next/link";
import { WritingPost } from "@/lib/types";

interface Props {
  post: WritingPost;
}

export default function WritingCitation({ post }: Props) {
  const isPreprint = !!post.DOI && /arxiv/i.test(post.DOI);
  return (
    <div className="mb-3">
      <p className="text-sm">
        {post.authors && <>{post.authors} </>}
        {(() => {
          const year = post.dates || (post.date ? post.date.slice(0, 4) : "");
          return year ? <>({year}). </> : null;
        })()}
        {isPreprint && (
          <span className="italic" style={{ color: "var(--text-muted)" }}>
            (preprint){" "}
          </span>
        )}
        <Link href={`/${post.year}/${post.month}/${post.slug}`} className="font-semibold">
          {post.title}
        </Link>
        .{" "}
        {post.sponsor && <>{post.sponsor}. </>}
        {post.pages && post.pages.trim() !== "" && <>{post.pages}. </>}
        {post.DOI && post.DOI.trim() !== "" && <>DOI={post.DOI}. </>}
        {post.editors && post.editors.trim() !== "" && <>{post.editors}. </>}
      </p>
    </div>
  );
}
