import React from 'react';
import { User, Cpu, Sparkles } from 'lucide-react';

/**
 * ChatMessage Component
 * Displays user prompts and Claude AI reasoning responses with evidence grounding badges.
 * Supports Markdown: ### Headings, **bold**, `code`, numbered lists (1. item), bullet lists (- item), and math cleanups.
 */
export default function ChatMessage({
  role = 'assistant',
  content = '',
  timestamp = null,
  modelName = 'claude-3-5-sonnet',
  isStreaming = false
}) {
  const isUser = role === 'user';
  const isSystem = role === 'system';

  const formattedTime = timestamp
    ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '';

  return (
    <div className={`flex w-full my-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[85%] md:max-w-[80%] space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center shadow-md ${
          isUser
            ? 'bg-gradient-to-tr from-cyan-600 to-blue-500 text-white'
            : isSystem
            ? 'bg-slate-700 text-slate-300'
            : 'bg-gradient-to-tr from-violet-600 to-fuchsia-600 text-white'
        }`}>
          {isUser ? <User className="w-4 h-4" /> : isSystem ? <Cpu className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
        </div>

        {/* Bubble */}
        <div className="flex flex-col">
          {/* Header */}
          <div className={`flex items-center space-x-2 text-[11px] mb-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <span className="font-semibold text-slate-300">
              {isUser ? 'Security Analyst' : isSystem ? 'System Event' : 'Claude UEBA Explainer'}
            </span>
            {!isUser && !isSystem && (
              <span className="text-[10px] font-mono text-violet-400 bg-violet-950/60 border border-violet-500/30 px-1.5 py-0.5 rounded">
                {modelName}
              </span>
            )}
            {formattedTime && (
              <span className="text-slate-500 text-[10px]">{formattedTime}</span>
            )}
          </div>

          {/* Body */}
          <div className={`p-4 rounded-2xl text-xs md:text-sm leading-relaxed font-sans space-y-1.5 ${
            isUser
              ? 'bg-blue-600 text-white rounded-tr-none shadow-[0_2px_10px_rgba(37,99,235,0.3)]'
              : isSystem
              ? 'bg-slate-800/80 text-slate-300 border border-slate-700 rounded-tl-none font-mono text-xs'
              : 'bg-slate-900/95 text-slate-200 border border-slate-700/80 rounded-tl-none shadow-[0_4px_20px_rgba(0,0,0,0.4)]'
          }`}>
            {renderMarkdown(content)}
            {isStreaming && (
              <span className="inline-block w-1.5 h-4 ml-1 bg-cyan-400 animate-pulse align-middle" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/** Clean up raw LaTeX-like tokens into clean readable Unicode */
function sanitizeMath(text) {
  if (!text) return '';
  return text
    .replace(/\$p_\{?\\text\{xgb\}\}?\$?/gi, 'p_xgb')
    .replace(/\$s_\{?\\text\{if\}\}?\$?/gi, 's_if')
    .replace(/\$d_\{?\\text\{peer\}\}?\$?/gi, 'd_peer')
    .replace(/\$D_\{?\\text\{drift\}\}?\$?/gi, 'D_drift')
    .replace(/\\tau_\{?\\text\{drift\}\}?/gi, 'τ_drift')
    .replace(/\\sigma/gi, 'σ')
    .replace(/\\ge/gi, '≥')
    .replace(/\\le/gi, '≤')
    .replace(/\$([^\$]+)\$/g, '$1');
}

/** Enhanced Markdown renderer for headings, lists, bold, and code blocks */
function renderMarkdown(rawText) {
  if (!rawText) return null;
  const text = sanitizeMath(rawText);

  return text.split('\n').map((line, lineIdx) => {
    const trimmed = line.trim();

    // 1. Headings (### or ##)
    if (trimmed.startsWith('### ') || trimmed.startsWith('## ')) {
      const headingText = trimmed.replace(/^#{2,3}\s+/, '');
      return (
        <div key={lineIdx} className="font-bold text-cyan-300 text-sm md:text-base pt-2 pb-1 border-b border-slate-800/80 mb-2">
          {renderInlineTokens(headingText)}
        </div>
      );
    }

    // 2. Numbered list items (e.g. 1. , 2. )
    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (numMatch) {
      const num = numMatch[1];
      const rest = numMatch[2];
      return (
        <div key={lineIdx} className="flex items-start gap-2.5 my-1.5 pl-1">
          <span className="w-5 h-5 rounded-full bg-violet-950/80 border border-violet-500/40 text-violet-300 font-mono text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
            {num}
          </span>
          <div className="flex-1 text-slate-200">
            {renderInlineTokens(rest)}
          </div>
        </div>
      );
    }

    // 3. Bullet list items (- or *)
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      const bulletContent = trimmed.slice(2);
      const isIndented = line.startsWith('   ') || line.startsWith('\t');
      return (
        <div key={lineIdx} className={`flex items-start gap-2 my-1 ${isIndented ? 'pl-6 text-slate-300' : 'pl-2 text-slate-200'}`}>
          <span className="text-cyan-400 font-bold shrink-0 mt-0.5">•</span>
          <div className="flex-1">
            {renderInlineTokens(bulletContent)}
          </div>
        </div>
      );
    }

    // 4. Empty line
    if (trimmed === '') {
      return <div key={lineIdx} className="h-1.5" />;
    }

    // 5. Standard paragraph line
    return (
      <div key={lineIdx} className="my-0.5 text-slate-300">
        {renderInlineTokens(line)}
      </div>
    );
  });
}

/** Renders bold, code, and italic inline tokens */
function renderInlineTokens(lineText) {
  if (!lineText) return null;

  return lineText.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-bold text-white tracking-wide">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={i} className="bg-slate-950 text-cyan-300 px-1.5 py-0.5 rounded border border-slate-800 text-[11px] font-mono">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}
