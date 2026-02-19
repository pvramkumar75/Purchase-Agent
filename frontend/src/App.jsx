import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
    Plus, Send, LayoutDashboard, MessageSquare, X, ArrowRight,
    ShieldCheck, Loader2, FileText, Sparkles, FolderOpen, Copy,
    Check, Bot, User, Square
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = 'http://localhost:8000';

/* ─── MARKDOWN COMPONENTS (Claude-quality rendering) ────────────── */
const mdComponents = {
    p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
    strong: ({ children }) => <strong className="font-bold text-slate-900">{children}</strong>,
    em: ({ children }) => <em className="text-slate-600 italic">{children}</em>,
    h1: ({ children }) => <h1 className="text-xl font-bold text-slate-900 mb-3 mt-4 first:mt-0">{children}</h1>,
    h2: ({ children }) => <h2 className="text-lg font-bold text-slate-900 mb-2 mt-4 first:mt-0">{children}</h2>,
    h3: ({ children }) => <h3 className="text-base font-bold text-slate-800 mb-2 mt-3 first:mt-0">{children}</h3>,
    ul: ({ children }) => <ul className="list-disc pl-5 mb-3 space-y-1.5">{children}</ul>,
    ol: ({ children }) => <ol className="list-decimal pl-5 mb-3 space-y-1.5">{children}</ol>,
    li: ({ children }) => <li className="text-sm leading-relaxed">{children}</li>,
    table: ({ children }) => (
        <div className="overflow-x-auto my-4 rounded-xl border border-slate-200 shadow-sm">
            <table className="min-w-full text-sm">{children}</table>
        </div>
    ),
    thead: ({ children }) => <thead className="bg-gradient-to-r from-slate-50 to-slate-100">{children}</thead>,
    th: ({ children }) => <th className="px-4 py-3 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-200">{children}</th>,
    td: ({ children }) => <td className="px-4 py-3 border-b border-slate-50 text-slate-700">{children}</td>,
    code: ({ inline, children }) => inline
        ? <code className="bg-slate-100 text-orange-700 px-1.5 py-0.5 rounded text-[13px] font-mono">{children}</code>
        : <pre className="bg-slate-900 text-green-400 p-4 rounded-xl overflow-x-auto text-[13px] font-mono my-3 shadow-inner"><code>{children}</code></pre>,
    blockquote: ({ children }) => <blockquote className="border-l-4 border-blue-400 pl-4 italic text-slate-600 my-3">{children}</blockquote>,
    hr: () => <hr className="my-4 border-slate-200" />,
};

/* ─── COPY BUTTON ────────────────────────────────────────────────── */
function CopyButton({ text }) {
    const [copied, setCopied] = useState(false);
    return (
        <button
            onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg hover:bg-slate-200 text-slate-400"
        >
            {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
        </button>
    );
}

/* ─── MAIN APP ───────────────────────────────────────────────────── */
function App() {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: `## ✨ Welcome to OmniMind

I'm your **universal operations assistant** with full, autonomous access to your computer.

### My Capabilities:
- 🔍 **Universal Search** — Locate any file across your D: drive, Desktop, or Downloads instantly.
- 🧠 **Document Intelligence** — Analyze invoices, reports, or legal docs (PDF, Excel, Word, OCR).
- 📁 **Smart Cleanup** — Sort cluttered downloads, organize project folders, or tidy your desktop.
- 📊 **Business Insight** — Specialized in procurement, price history, and vendor comparisons.
- ⚙️ **Process Automation** — Draft emails, summarize long papers, and proactively organize your digital life.

**Ask me something like:**
> "Find all 2024 tax documents on my D drive"
> "Tidy up my Downloads folder by grouping files by type"
> "Summarize the latest quote from the 'capex25' folder"`
        }
    ]);
    const [input, setInput] = useState('');
    const [isDashboardOpen, setIsDashboardOpen] = useState(false);
    const [quotes, setQuotes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [duration, setDuration] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const timerRef = useRef(null);
    const fileInputRef = useRef(null);
    const chatEndRef = useRef(null);
    const textareaRef = useRef(null);
    const abortControllerRef = useRef(null);

    useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);
    useEffect(() => { fetchQuotes(); }, []);

    const fetchQuotes = async () => {
        try { const res = await axios.get(`${API_URL}/quotes`); setQuotes(res.data); }
        catch (err) { console.error("Fetch error:", err); }
    };

    const lastMessageRef = useRef('');

    const handleStop = () => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setLoading(false);
            if (timerRef.current) clearInterval(timerRef.current);

            // Restore last message to input for easy correction
            setInput(lastMessageRef.current);

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '_Process interrupted. Your command has been restored to the input box for correction._'
            }]);
        }
    };

    const handleSendMessage = async () => {
        if (!input.trim() || loading) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        const currentInput = input;
        lastMessageRef.current = input; // Store for potential interruption
        setInput('');
        setLoading(true);
        setDuration(0);

        // Start live timer
        timerRef.current = setInterval(() => {
            setDuration(prev => Math.round((prev + 0.1) * 10) / 10);
        }, 100);

        // Create AbortController
        abortControllerRef.current = new AbortController();

        try {
            const res = await axios.post(`${API_URL}/chat`, {
                query: currentInput,
                history: messages.map(m => ({ role: m.role, content: m.content }))
            }, {
                signal: abortControllerRef.current.signal
            });
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: res.data.reply,
                duration: res.data.duration
            }]);
            fetchQuotes();
        } catch (err) {
            if (axios.isCancel(err)) {
                console.log("Request canceled");
            } else {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: `⚠️ **Connection Error**\n\nI couldn't reach the OmniMind engine. Please ensure:\n1. Docker containers are running (\`docker-compose up\`)\n2. Backend is accessible at \`${API_URL}\`\n\nError: \`${err.message}\``
                }]);
            }
        } finally {
            setLoading(false);
            if (timerRef.current) clearInterval(timerRef.current);
            abortControllerRef.current = null;
        }
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setMessages(prev => [...prev, { role: 'user', content: `📎 Processing **${file.name}**...` }]);
        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await axios.post(`${API_URL}/upload`, formData);
            const analysis = res.data.analysis || {};
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `## ✅ File Processed: ${file.name}

**Type:** ${analysis.type || 'General Knowledge'}

${analysis.summary || 'Document has been analyzed and indexed in your local memory.'}`
            }]);
            fetchQuotes();
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `❌ **Processing Failed**\n\nCould not handle \`${file.name}\`. Error: \`${err.message}\``
            }]);
        } finally {
            setIsUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    // Auto-resize textarea
    const handleTextareaChange = (e) => {
        setInput(e.target.value);
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
        }
    };

    return (
        <div className="flex h-screen bg-white text-slate-800 overflow-hidden" style={{ fontFamily: "'Inter', -apple-system, sans-serif" }}>
            {/* ─── Sidebar ────────────────────────────────────────────── */}
            <div className="w-[60px] bg-slate-50 border-r border-slate-100 flex flex-col items-center py-5 gap-3 shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-200/50 mb-4">
                    <Sparkles size={20} />
                </div>
                <SidebarBtn icon={<MessageSquare size={18} />} active={!isDashboardOpen} onClick={() => setIsDashboardOpen(false)} label="Brain" />
                <SidebarBtn icon={<LayoutDashboard size={18} />} active={isDashboardOpen} onClick={() => setIsDashboardOpen(true)} label="Dashboard" />
                <SidebarBtn icon={<FolderOpen size={18} />} onClick={() => {
                    setInput("Show me my folder structure across D drive and Desktop");
                    setTimeout(() => handleSendMessage(), 100);
                }} label="Filesystem" />
                <div className="mt-auto">
                    <div className="p-2 text-slate-300" title="100% Private - Air Gapped Memory">
                        <ShieldCheck size={18} />
                    </div>
                </div>
            </div>

            {/* ─── Main Chat ──────────────────────────────────────────── */}
            <div className="flex-1 flex flex-col bg-white min-w-0">
                {/* Header */}
                <div className="h-14 border-b border-slate-100 flex items-center px-6 shrink-0 bg-white/80 backdrop-blur-sm">
                    <div className="flex items-center gap-3">
                        <span className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></span>
                        <span className="text-sm font-semibold text-slate-700 uppercase tracking-tight">OmniMind</span>
                        <span className="text-[10px] px-2 py-0.5 bg-indigo-50 rounded-full text-indigo-400 font-bold uppercase">v3.0 Alpha</span>
                    </div>
                </div>

                {/* Message Stream */}
                <div className="flex-1 overflow-y-auto">
                    <div className="max-w-3xl mx-auto py-6 px-6 space-y-6">
                        {messages.map((msg, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 8 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.2, delay: 0.05 }}
                                className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}
                            >
                                {msg.role === 'assistant' && (
                                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shrink-0 mt-1 shadow-sm">
                                        <Bot size={14} />
                                    </div>
                                )}
                                <div className={`group relative max-w-[88%] ${msg.role === 'user'
                                    ? 'bg-slate-800 text-white rounded-2xl rounded-br-md px-5 py-3 shadow-lg'
                                    : 'bg-white text-slate-800 rounded-2xl rounded-bl-md px-5 py-4 border border-slate-100 shadow-sm'
                                    }`}>
                                    {msg.role === 'user' ? (
                                        <div className="text-sm leading-relaxed whitespace-pre-wrap">
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}
                                                components={{
                                                    ...mdComponents,
                                                    strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
                                                    p: ({ children }) => <p className="mb-1 last:mb-0">{children}</p>,
                                                }}
                                            >{msg.content}</ReactMarkdown>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="text-sm">
                                                <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                                                    {msg.content}
                                                </ReactMarkdown>
                                            </div>
                                            <div className="absolute -bottom-3 right-2 flex items-center gap-2">
                                                {msg.duration && (
                                                    <span className="text-[10px] bg-slate-100 text-slate-400 px-1.5 py-0.5 rounded-md font-mono">
                                                        {msg.duration}s
                                                    </span>
                                                )}
                                                <CopyButton text={msg.content} />
                                            </div>
                                        </>
                                    )}
                                </div>
                                {msg.role === 'user' && (
                                    <div className="w-8 h-8 rounded-lg bg-slate-200 flex items-center justify-center text-slate-600 shrink-0 mt-1">
                                        <User size={14} />
                                    </div>
                                )}
                            </motion.div>
                        ))}

                        {loading && (
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4">
                                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shrink-0 shadow-sm">
                                    <Loader2 size={14} className="animate-spin" />
                                </div>
                                <div className="bg-white border border-slate-100 rounded-2xl rounded-bl-md px-5 py-4 shadow-sm">
                                    <div className="flex items-center gap-3">
                                        <div className="flex gap-1">
                                            <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                            <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                            <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                        </div>
                                        <span className="text-sm text-slate-400 italic">
                                            Analyzing and reasoning... ({duration}s)
                                        </span>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                        <div ref={chatEndRef} />
                    </div>
                </div>

                {/* ─── Input Bar ────────────────────────────────────────── */}
                <div className="border-t border-slate-100 bg-white px-6 py-4 shrink-0">
                    <div className="max-w-3xl mx-auto">
                        <div className="relative bg-slate-50 rounded-2xl border border-slate-200 focus-within:border-blue-300 focus-within:ring-4 focus-within:ring-blue-500/5 transition-all shadow-sm">
                            <div className="flex items-end gap-2 p-2">
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="p-2 hover:bg-white rounded-xl text-slate-400 hover:text-slate-600 transition-all shrink-0 mb-0.5"
                                    disabled={isUploading}
                                    title="Attach file (PDF, Excel, Word, Image)"
                                >
                                    {isUploading ? <Loader2 size={20} className="animate-spin" /> : <Plus size={20} />}
                                </button>
                                <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden"
                                    accept=".pdf,.docx,.doc,.xlsx,.xls,.csv,.txt,.jpg,.jpeg,.png,.bmp,.tiff" />
                                <textarea
                                    ref={textareaRef}
                                    placeholder="Ask me anything — search files, analyze quotes, organize folders..."
                                    className="flex-1 bg-transparent py-2 px-1 focus:outline-none resize-none text-sm text-slate-800 placeholder:text-slate-400 min-h-[40px] max-h-[200px]"
                                    rows={1}
                                    value={input}
                                    onChange={handleTextareaChange}
                                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); } }}
                                />
                                {loading && (
                                    <button
                                        onClick={handleStop}
                                        className="p-2 rounded-xl bg-red-50 text-red-500 hover:bg-red-100 transition-all shrink-0 mb-0.5 shadow-sm border border-red-100 flex items-center gap-1.5 px-3"
                                        title="Stop current process"
                                    >
                                        <Square size={14} fill="currentColor" />
                                        <span className="text-xs font-bold uppercase tracking-wider">Stop</span>
                                    </button>
                                )}
                                <button
                                    onClick={handleSendMessage}
                                    disabled={!input.trim() || loading}
                                    className={`p-2 rounded-xl transition-all shrink-0 mb-0.5 ${input.trim() && !loading
                                        ? 'bg-blue-600 text-white shadow-md shadow-blue-200/50 hover:bg-blue-700'
                                        : 'bg-slate-200 text-slate-400'
                                        }`}
                                >
                                    <Send size={18} />
                                </button>
                            </div>
                        </div>
                        <div className="flex justify-center gap-6 mt-3">
                            <FooterTag>🔒 Local-First Privacy</FooterTag>
                            <FooterTag>🧠 Persistent Memory</FooterTag>
                            <FooterTag>📁 Full Disk Access</FooterTag>
                        </div>
                    </div>
                </div>
            </div>

            {/* ─── Dashboard Panel ────────────────────────────────────── */}
            <AnimatePresence>
                {isDashboardOpen && (
                    <motion.div
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 440, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                        className="bg-slate-50 border-l border-slate-100 flex flex-col overflow-hidden shrink-0"
                    >
                        {/* Dashboard Header */}
                        <div className="p-6 border-b border-slate-100 flex justify-between items-center shrink-0">
                            <div>
                                <h2 className="text-lg font-bold text-slate-900">Analyst Hub</h2>
                                <div className="flex items-center gap-2 mt-0.5">
                                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                                    <p className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Memory Active • {quotes.length} Records</p>
                                </div>
                            </div>
                            <button onClick={() => setIsDashboardOpen(false)} className="p-2 hover:bg-white rounded-xl text-slate-400 transition-all">
                                <X size={18} />
                            </button>
                        </div>

                        {/* Stats */}
                        <div className="p-6 space-y-5 flex-1 overflow-y-auto">
                            <div className="grid grid-cols-2 gap-3">
                                <StatCard label="Quotes" value={quotes.length} color="bg-white border border-slate-200" />
                                <StatCard label="Vendors" value={[...new Set(quotes.map(q => q.vendor_name))].length} color="bg-blue-600 text-white" light />
                            </div>

                            {/* Quote Cards */}
                            <div>
                                <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4">Recent Quotes</h3>
                                {quotes.length === 0 ? (
                                    <div className="py-16 text-center">
                                        <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center mx-auto text-slate-300 border border-slate-100 mb-4">
                                            <FileText size={24} />
                                        </div>
                                        <p className="text-slate-400 text-sm">No quotes yet.</p>
                                        <p className="text-slate-300 text-xs mt-1">Upload a document to get started.</p>
                                    </div>
                                ) : quotes.slice(0, 10).map((q, idx) => (
                                    <motion.div
                                        key={q.id || idx}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: idx * 0.05 }}
                                        className="bg-white border border-slate-100 rounded-2xl p-5 mb-3 hover:shadow-md hover:border-slate-200 transition-all cursor-pointer"
                                    >
                                        <div className="flex justify-between items-start mb-2">
                                            <p className="font-bold text-sm text-slate-900 leading-tight">{q.vendor_name || 'Unknown Vendor'}</p>
                                            <span className="text-[11px] bg-blue-50 text-blue-700 px-2.5 py-1 rounded-lg font-bold whitespace-nowrap">
                                                {q.currency || ''} {q.total || '—'}
                                            </span>
                                        </div>
                                        <p className="text-xs text-slate-500 mb-3">{q.material || 'Material not specified'}</p>
                                        <div className="flex gap-4 pt-3 border-t border-slate-50 text-[10px]">
                                            <div>
                                                <span className="text-slate-400 uppercase tracking-wider font-semibold block">Delivery</span>
                                                <span className="text-slate-700 font-bold">{q.delivery_weeks ? `${q.delivery_weeks}W` : '—'}</span>
                                            </div>
                                            <div>
                                                <span className="text-slate-400 uppercase tracking-wider font-semibold block">Terms</span>
                                                <span className="text-slate-700 font-bold">{q.payment_terms || '—'}</span>
                                            </div>
                                            <div>
                                                <span className="text-slate-400 uppercase tracking-wider font-semibold block">Date</span>
                                                <span className="text-slate-700 font-bold">{q.date || '—'}</span>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                        {/* Dashboard Footer */}
                        <div className="p-4 border-t border-slate-100 shrink-0">
                            <button
                                onClick={() => { setInput("Generate a comparison report for all stored quotes"); setIsDashboardOpen(false); }}
                                className="w-full bg-slate-900 text-white py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 hover:bg-black transition-all shadow-lg shadow-slate-200/50"
                            >
                                Generate Report <ArrowRight size={16} />
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

/* ─── Sub-Components ─────────────────────────────────────────────── */
function SidebarBtn({ icon, active, onClick, label }) {
    return (
        <button
            onClick={onClick}
            title={label}
            className={`p-2.5 rounded-xl transition-all ${active ? 'bg-white text-blue-600 shadow-sm border border-slate-100' : 'text-slate-400 hover:bg-white hover:text-slate-600'
                }`}
        >
            {icon}
        </button>
    );
}

function StatCard({ label, value, color, light }) {
    return (
        <div className={`p-5 rounded-2xl ${color} ${light ? '' : 'shadow-sm'}`}>
            <p className={`text-[10px] font-bold uppercase tracking-widest ${light ? 'text-blue-200' : 'text-slate-400'}`}>{label}</p>
            <p className={`text-3xl font-bold mt-1 ${light ? 'text-white' : 'text-slate-900'}`}>{value}</p>
        </div>
    );
}

function FooterTag({ children }) {
    return <span className="text-[10px] text-slate-400 font-medium">{children}</span>;
}

export default App;
