import type { Chapter4Content } from "@/types/document";

export interface Chapter4Props {
  content: Chapter4Content;
}

/**
 * Chapter4 (T104): "Line-by-Line Explanation" — one block per source line,
 * showing its line number, the code itself, a plain-language explanation,
 * a real-world analogy, an alternative example, and extra notes.
 */
export default function Chapter4({ content }: Chapter4Props) {
  return (
    <section>
      <h2>{content.title}</h2>
      <div>
        {content.explanations.map((explanation) => (
          <article key={explanation.line}>
            <span data-testid="chapter4-line-number">{explanation.line}</span>
            <pre>{explanation.code}</pre>
            <p>{explanation.explanation}</p>
            <p>{explanation.analogy}</p>
            <pre>{explanation.alternativeExample}</pre>
            <p>{explanation.notes}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
