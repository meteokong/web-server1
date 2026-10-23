import { useState } from "react";
import type { DocumentContent } from "@/types/document";
import Chapter1 from "./chapters/Chapter1";
import Chapter2 from "./chapters/Chapter2";
import Chapter4 from "./chapters/Chapter4";

export interface ExplanationPanelProps {
  content: DocumentContent;
}

type ChapterKey = keyof DocumentContent;

const CHAPTER_KEYS: ChapterKey[] = [
  "chapter1",
  "chapter2",
  "chapter3",
  "chapter4",
  "chapter5",
  "chapter6",
  "chapter7",
];

/**
 * ExplanationPanel (T101): chapter navigation (one button per chapter,
 * labeled by that chapter's title) plus the currently selected chapter's
 * content. Chapters 1/2/4 use their dedicated components (T102/T103/T104);
 * chapters 3/5/6/7 don't have dedicated components per tasks.md, so they're
 * rendered here with a generic title + structured-fields layout.
 */
export default function ExplanationPanel({ content }: ExplanationPanelProps) {
  const [activeChapter, setActiveChapter] = useState<ChapterKey>("chapter1");

  return (
    <div>
      <nav>
        {CHAPTER_KEYS.map((key) => (
          <button
            key={key}
            type="button"
            aria-current={activeChapter === key}
            onClick={() => setActiveChapter(key)}
          >
            {content[key].title}
          </button>
        ))}
      </nav>

      <div>{renderChapter(activeChapter, content)}</div>
    </div>
  );
}

function renderChapter(key: ChapterKey, content: DocumentContent) {
  switch (key) {
    case "chapter1":
      return <Chapter1 content={content.chapter1} />;
    case "chapter2":
      return <Chapter2 content={content.chapter2} />;
    case "chapter4":
      return <Chapter4 content={content.chapter4} />;
    case "chapter3": {
      const { title, flowchart, fileBreakdown } = content.chapter3;
      return (
        <section>
          <h2>{title}</h2>
          <pre>{flowchart}</pre>
          <dl>
            {Object.entries(fileBreakdown).map(([fileName, description]) => (
              <div key={fileName}>
                <dt>{fileName}</dt>
                <dd>{description}</dd>
              </div>
            ))}
          </dl>
        </section>
      );
    }
    case "chapter5": {
      const { title, steps } = content.chapter5;
      return (
        <section>
          <h2>{title}</h2>
          <ol>
            {steps.map((step) => (
              <li key={step.step}>{step.description}</li>
            ))}
          </ol>
        </section>
      );
    }
    case "chapter6": {
      const { title, concepts } = content.chapter6;
      return (
        <section>
          <h2>{title}</h2>
          {concepts.map((concept) => (
            <article key={concept.name}>
              <h3>{concept.name}</h3>
              <p>{concept.whatItIs}</p>
              <p>{concept.whyItsUsed}</p>
              <p>{concept.whereItsApplied}</p>
            </article>
          ))}
        </section>
      );
    }
    case "chapter7": {
      const { title, mistakes } = content.chapter7;
      return (
        <section>
          <h2>{title}</h2>
          {mistakes.map((mistake) => (
            <article key={mistake.wrong}>
              <p>{mistake.wrong}</p>
              <p>{mistake.right}</p>
              <p>{mistake.why}</p>
              <p>{mistake.fix}</p>
            </article>
          ))}
        </section>
      );
    }
    default:
      return null;
  }
}
