import type { Chapter2Content } from "@/types/document";

export interface Chapter2Props {
  content: Chapter2Content;
}

/**
 * Chapter2 (T103): "Prerequisites Knowledge" — a card per concept, each
 * showing its name, explanation, a real-world analogy, a code example, and
 * typical use cases.
 */
export default function Chapter2({ content }: Chapter2Props) {
  return (
    <section>
      <h2>{content.title}</h2>
      <div>
        {content.concepts.map((concept) => (
          <article key={concept.name}>
            <h3>{concept.name}</h3>
            <p>{concept.explanation}</p>
            <p>{concept.analogy}</p>
            <pre>{concept.example}</pre>
            <p>{concept.useCases}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
