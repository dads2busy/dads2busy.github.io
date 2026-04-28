import Link from "next/link";
import { WritingPost } from "@/lib/types";

interface Props {
  post: WritingPost;
}

export default function WritingCitation({ post }: Props) {
  return (
    <div className="mb-3">
      <p className="text-sm">
        {post.authors && <>{post.authors} </>}
        {(() => {
          const year = post.dates || (post.date ? post.date.slice(0, 4) : "");
          return year ? <>({year}). </> : null;
        })()}
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
