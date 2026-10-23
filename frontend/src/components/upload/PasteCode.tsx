import { useId, useState } from "react";

export interface PasteCodeValues {
  code: string;
  language: string;
}

export interface PasteCodeProps {
  /** Called with the current code/language whenever either changes. */
  onChange: (values: PasteCodeValues) => void;
}

/** Options mirror the backend's language_detector.EXTENSION_TO_LANGUAGE values. */
const LANGUAGE_OPTIONS: { value: string; label: string }[] = [
  { value: "python", label: "Python" },
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
  { value: "java", label: "Java" },
  { value: "cpp", label: "C++" },
  { value: "c", label: "C" },
  { value: "html", label: "HTML" },
  { value: "css", label: "CSS" },
  { value: "text", label: "Text" },
  { value: "markdown", label: "Markdown" },
];

/**
 * "코드 붙여넣기" upload method for CreateTaskModal (T081): a code textarea
 * plus a language select. Reports the combined {code, language} up on every
 * change rather than owning the submitted value itself.
 */
export function PasteCode({ onChange }: PasteCodeProps) {
  const codeId = useId();
  const languageId = useId();
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState(LANGUAGE_OPTIONS[0].value);

  return (
    <div>
      <div>
        <label htmlFor={codeId}>코드</label>
        <textarea
          id={codeId}
          value={code}
          onChange={(e) => {
            setCode(e.target.value);
            onChange({ code: e.target.value, language });
          }}
        />
      </div>
      <div>
        <label htmlFor={languageId}>언어</label>
        <select
          id={languageId}
          value={language}
          onChange={(e) => {
            setLanguage(e.target.value);
            onChange({ code, language: e.target.value });
          }}
        >
          {LANGUAGE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
