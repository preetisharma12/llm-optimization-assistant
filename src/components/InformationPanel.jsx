import { TreePine, Image as ImageIcon, FileText } from "lucide-react";

// ==========================
// Build the flat list of lines (with tree-branch prefixes)
// needed to render concepts + their items as an ASCII tree.
// ==========================
function buildTreeLines(concepts) {
  const lines = [];

  concepts.forEach((concept, i) => {
    const isLastConcept = i === concepts.length - 1;
    const items = concept.items || [];

    lines.push({
      type: "spacer",
      prefix: isLastConcept && items.length === 0 ? " " : "│",
    });

    lines.push({
      type: "concept",
      prefix: isLastConcept ? "└── " : "├── ",
      concept,
    });

    const childPrefix = isLastConcept ? "    " : "│   ";

    items.forEach((item, j) => {
      const isLastItem = j === items.length - 1;
      lines.push({
        type: "item",
        prefix: childPrefix + (isLastItem ? "└── " : "├── "),
        item,
        concept,
      });
    });
  });

  return lines;
}

function InformationPanel({ info }) {

  const concepts = info.concepts || [];

  const explanationLines = info.explanation
    ? info.explanation.split(/(?<=[.!?])\s+/).filter(Boolean)
    : [];

  return (
    <div className="w-[380px] bg-slate-100 border-l border-slate-200 flex flex-col gap-4 p-4 overflow-y-auto overflow-x-hidden">

      {/* Concept Tree */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
        <div className="flex items-center gap-2 mb-4">
          <TreePine size={18} className="text-emerald-600" />
          <h2 className="font-bold text-slate-800">Problem / Concept Tree</h2>
        </div>

        {concepts.length === 0 ? (
          <div className="text-slate-400 text-sm font-mono">Waiting...</div>
        ) : (
          <div className="font-mono text-[13px] leading-6 min-w-0">
            <div className="text-slate-800 font-semibold mb-0.5 break-words">
              {info.problemTitle || "Optimization Problem"}
            </div>

            {buildTreeLines(concepts).map((line, i) => {
              if (line.type === "spacer") {
                return (
                  <div key={i} className="text-slate-300 whitespace-pre">
                    {line.prefix}
                  </div>
                );
              }

              if (line.type === "concept") {
                const isCurrent = line.concept.status === "current";
                const isCompleted = line.concept.status === "completed";

                return (
                  <div
                    key={i}
                    className={`flex items-start gap-2 min-w-0 rounded ${
                      isCurrent
                        ? "bg-blue-50 border-l-2 border-blue-500 -ml-2 pl-[6px] pr-1"
                        : ""
                    }`}
                  >
                    <span className="text-slate-300 shrink-0 whitespace-pre">
                      {line.prefix}
                    </span>
                    <div className="min-w-0 flex-1 flex flex-wrap items-baseline gap-x-2">
                      <span
                        className={`break-words ${
                          isCurrent
                            ? "text-blue-700 font-bold"
                            : isCompleted
                            ? "text-slate-800 font-semibold"
                            : "text-slate-400"
                        }`}
                      >
                        {line.concept.name}
                      </span>
                      {isCurrent && (
                        <span className="flex items-center gap-1 text-[10px] font-semibold text-blue-600 uppercase tracking-wide">
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse shrink-0" />
                          Now discussing
                        </span>
                      )}
                    </div>
                  </div>
                );
              }

              // item line
              const isCurrent = line.concept.status === "current";

              return (
                <div key={i} className="flex items-start gap-2 min-w-0">
                  <span className="text-slate-300 shrink-0 whitespace-pre">
                    {line.prefix}
                  </span>
                  <div className="min-w-0 flex-1 flex flex-wrap items-baseline gap-x-1.5">
                    <span
                      className={`break-words ${
                        isCurrent ? "text-blue-600" : "text-slate-500"
                      }`}
                    >
                      {line.item.name}
                    </span>
                    {line.item.class && (
                      <span className="text-slate-400 text-[11px] shrink-0">
                        ({line.item.class})
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* AI-Generated Image */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
        <div className="flex items-center gap-2 mb-4">
          <ImageIcon size={18} className="text-amber-600" />
          <h2 className="font-bold text-slate-800">AI-Generated Image</h2>
        </div>

        <div className="border-2 border-dashed border-slate-300 rounded-xl h-40 flex items-center justify-center text-slate-400 text-sm bg-slate-50">
          Relevant system image
        </div>
      </div>

      {/* Explanation */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
        <div className="flex items-center gap-2 mb-4">
          <FileText size={18} className="text-slate-600" />
          <h2 className="font-bold text-slate-800">Explanation</h2>
        </div>

        <div className="space-y-2 text-sm text-slate-700">
          {explanationLines.length > 0 ? (
            explanationLines.map((sentence, i) => (
              <p key={i} className="italic">"{sentence.trim()}"</p>
            ))
          ) : (
            <p className="text-slate-400">Waiting...</p>
          )}
        </div>
      </div>

      {/* Attributes & Progress */}
      {(info.attributes?.length > 0 || info.progress) && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          {info.attributes && info.attributes.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {info.attributes.map((attribute, i) => (
                <span
                  key={i}
                  className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full"
                >
                  {attribute}
                </span>
              ))}
            </div>
          )}

          <p className="text-xs text-slate-400">
            Progress: {info.progress || "0 / 0 completed"}
          </p>
        </div>
      )}

    </div>
  );
}

export default InformationPanel;