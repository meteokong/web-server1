import type { Chapter1Content } from "@/types/document";

export interface Chapter1Props {
  content: Chapter1Content;
}

/** Chapter1 (T102): "What This Code Does" — a title and a one-sentence summary. */
export default function Chapter1({ content }: Chapter1Props) {
  return (
    <section>
      <h2>{content.title}</h2>
      <p>{content.summary}</p>
    </section>
  );
}
