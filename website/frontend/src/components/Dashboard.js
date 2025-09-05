import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  User, 
  LogOut, 
  MessageCircle, 
  Plus, 
  Send, 
  Calendar,
  PenTool,
  ChevronRight,
  CheckCircle2,
  HelpCircle,
  Download,
  X,
  AlertCircle
} from 'lucide-react';
import DailyBriefing from './DailyBriefing';
import ThemeToggle from './ThemeToggle';
import { useWalkthrough } from '../contexts/WalkthroughContext';

// Configure axios base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for RAG processing
});

const Dashboard = ({ setIsAuthenticated }) => {
  const [showBriefing, setShowBriefing] = useState(false);
  const [query, setQuery] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [note, setNote] = useState('');
  const [isSubmittingNote, setIsSubmittingNote] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showLogoModal, setShowLogoModal] = useState(false);
  
  const { restartWalkthrough } = useWalkthrough();
  const chatContainerRef = useRef(null);

  // OrbitAI Logo SVG
  const orbitAISVG = `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <style>
        .orbit-ring { fill: none; stroke: currentColor; stroke-width: 3; }
        .orbit-node { fill: currentColor; }
        .center-node { fill: currentColor; }
        .brand-text { font-family: 'Arial', sans-serif; font-weight: bold; }
      </style>
    </defs>
    
    <!-- Outer Ring -->
    <circle cx="100" cy="100" r="80" class="orbit-ring"/>
    
    <!-- Inner hexagonal structure with nodes -->
    <g transform="translate(100,100)">
      <!-- Central node -->
      <circle cx="0" cy="0" r="8" class="center-node"/>
      
      <!-- Hexagon connection lines -->
      <line x1="0" y1="0" x2="0" y2="-40" class="orbit-ring"/>
      <line x1="0" y1="0" x2="34.6" y2="-20" class="orbit-ring"/>
      <line x1="0" y1="0" x2="34.6" y2="20" class="orbit-ring"/>
      <line x1="0" y1="0" x2="0" y2="40" class="orbit-ring"/>
      <line x1="0" y1="0" x2="-34.6" y2="20" class="orbit-ring"/>
      <line x1="0" y1="0" x2="-34.6" y2="-20" class="orbit-ring"/>
      
      <!-- Outer hexagon connections -->
      <line x1="0" y1="-40" x2="34.6" y2="-20" class="orbit-ring"/>
      <line x1="34.6" y1="-20" x2="34.6" y2="20" class="orbit-ring"/>
      <line x1="34.6" y1="20" x2="0" y2="40" class="orbit-ring"/>
      <line x1="0" y1="40" x2="-34.6" y2="20" class="orbit-ring"/>
      <line x1="-34.6" y1="20" x2="-34.6" y2="-20" class="orbit-ring"/>
      <line x1="-34.6" y1="-20" x2="0" y2="-40" class="orbit-ring"/>
      
      <!-- Outer nodes -->
      <circle cx="0" cy="-40" r="6" class="orbit-node"/>
      <circle cx="34.6" cy="-20" r="6" class="orbit-node"/>
      <circle cx="34.6" cy="20" r="6" class="orbit-node"/>
      <circle cx="0" cy="40" r="6" class="orbit-node"/>
      <circle cx="-34.6" cy="20" r="6" class="orbit-node"/>
      <circle cx="-34.6" cy="-20" r="6" class="orbit-node"/>
    </g>
    
    <!-- Brand text -->
    <text x="100" y="160" text-anchor="middle" class="brand-text" style="font-size: 24px; fill: currentColor;">OrbitAI</text>
  </svg>`;

  const downloadSVG = () => {
    const blob = new Blob([orbitAISVG], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'OrbitAI-Logo.svg';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages, isThinking]);

  const handleLogout = () => {
    setIsAuthenticated(false);
  };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || isThinking) return;

    const userMessage = { 
      type: 'user', 
      text: query.trim(), 
      timestamp: new Date() 
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    const currentQuery = query.trim();
    setQuery('');
    setIsThinking(true);

    try {
      console.log('Sending query to backend:', currentQuery);
      
      const response = await api.post('/chat', {
        query: currentQuery
      });

      console.log('Backend response:', response.data);

      const botResponse = { 
        type: 'bot', 
        text: response.data.response || 'Sorry, I received an empty response.',
        timestamp: new Date(),
        error: response.data.error || null
      };
      
      setChatMessages(prev => [...prev, botResponse]);

    } catch (error) {
      console.error('Chat API error:', error);
      
      let errorMessage = 'Sorry, I encountered an error while processing your request.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'The request timed out. Please try again with a simpler question.';
      } else if (error.response) {
        // Server responded with error status
        errorMessage = `Server error (${error.response.status}): ${error.response.data?.detail || 'Please try again.'}`;
      } else if (error.request) {
        // Request made but no response received
        errorMessage = 'Unable to connect to the server. Please check your connection.';
      }

      const errorResponse = { 
        type: 'bot', 
        text: errorMessage,
        timestamp: new Date(),
        isError: true
      };
      
      setChatMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsThinking(false);
    }
  };

  const handleNoteSubmit = async (e) => {
    e.preventDefault();
    if (!note.trim()) return;

    setIsSubmittingNote(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsSubmittingNote(false);
      setNote('');
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 2000);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-14">
            <div className="flex items-center space-x-3">
              <button 
                onClick={() => setShowLogoModal(true)}
                className="w-10 h-10 rounded-lg bg-background border border-border flex items-center justify-center p-1 hover:scale-105 transition-transform duration-200 cursor-pointer"
              >
                <img 
                  src="/logo.png" 
                  alt="OrbitAI Logo" 
                  className="w-full h-full object-contain"
                />
              </button>
              <h1 className="text-lg font-semibold text-foreground">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div data-tour="theme-toggle">
                <ThemeToggle />
              </div>
              <button
                onClick={restartWalkthrough}
                className="flex items-center space-x-2 text-muted-foreground hover:text-foreground px-2 py-1.5 rounded-lg hover:bg-muted/50 transition-all duration-200"
                title="Restart Tour"
              >
                <HelpCircle className="h-4 w-4" />
              </button>
              <div className="flex items-center space-x-3 px-3 py-1.5 rounded-lg hover:bg-muted/50 transition-colors duration-200">
                <div className="w-7 h-7 rounded-full bg-muted flex items-center justify-center">
                  <User className="h-4 w-4 text-muted-foreground" />
                </div>
                <span className="text-sm font-medium text-foreground">Yuvanesh S</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 text-muted-foreground hover:text-foreground px-3 py-1.5 rounded-lg hover:bg-muted/50 transition-all duration-200"
              >
                <LogOut className="h-4 w-4" />
                <span className="text-sm">Sign out</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Daily Briefing Card */}
          <div 
            data-tour="daily-briefing"
            className="group border border-border rounded-xl p-6 hover:shadow-md transition-all duration-200 hover:border-foreground/20 bg-card"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center group-hover:bg-foreground/10 transition-colors duration-200">
                  <Calendar className="h-5 w-5 text-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Daily Briefing</h3>
                  <p className="text-sm text-muted-foreground">Your personalized overview</p>
                </div>
              </div>
              <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground group-hover:translate-x-0.5 transition-all duration-200" />
            </div>
            <button
              onClick={() => setShowBriefing(true)}
              className="w-full text-left p-3 rounded-lg border border-dashed border-muted-foreground/30 hover:border-foreground/50 hover:bg-muted/30 transition-all duration-200 text-sm text-muted-foreground hover:text-foreground"
            >
              View today's events, tasks, and insights
            </button>
          </div>

          {/* Quick Notes Card */}
          <div 
            data-tour="quick-notes"
            className="border border-border rounded-xl p-6 hover:shadow-md transition-all duration-200 hover:border-foreground/20 bg-card"
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                <PenTool className="h-5 w-5 text-foreground" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Quick Note</h3>
                <p className="text-sm text-muted-foreground">Capture your thoughts</p>
              </div>
            </div>
            <form onSubmit={handleNoteSubmit} className="space-y-3">
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Write a note..."
                className="w-full px-3 py-2 text-sm bg-background border border-border rounded-lg placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-foreground/20 focus:border-foreground transition-all duration-200 resize-none"
                rows="3"
              />
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {showSuccess && (
                    <div className="flex items-center space-x-1 text-green-600 dark:text-green-400 animate-in slide-in-from-left-2 duration-200">
                      <CheckCircle2 className="h-4 w-4" />
                      <span className="text-xs">Saved</span>
                    </div>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={isSubmittingNote || !note.trim()}
                  className="flex items-center space-x-1 bg-foreground text-background hover:bg-foreground/90 disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed text-xs font-medium px-3 py-1.5 rounded-md transition-all duration-200 transform hover:translate-y-[-1px] active:translate-y-0 disabled:transform-none"
                >
                  <Plus className="h-3 w-3" />
                  <span>{isSubmittingNote ? 'Saving...' : 'Add'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* AI Assistant */}
        <div 
          data-tour="ai-assistant"
          className="border border-border rounded-xl bg-card overflow-hidden"
        >
          <div className="p-6 border-b border-border">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                <MessageCircle className="h-5 w-5 text-foreground" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">AI Assistant</h3>
                <p className="text-sm text-muted-foreground">Ask about your emails, calendar, weather, and news</p>
              </div>
            </div>
          </div>
          
          {/* Chat Messages */}
          <div 
            ref={chatContainerRef}
            className="p-6 space-y-4 max-h-96 overflow-y-auto scroll-smooth"
            style={{ scrollBehavior: 'smooth' }}
          >
            {chatMessages.length === 0 && (
              <div className="text-center py-8">
                <p className="text-muted-foreground text-sm mb-2">Start a conversation by asking a question below</p>
                <p className="text-xs text-muted-foreground">Try: "What are my recent emails?" or "What's the weather today?"</p>
              </div>
            )}
            
            {chatMessages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2 duration-300`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg text-sm ${
                    message.type === 'user'
                      ? 'bg-foreground text-background'
                      : message.isError
                      ? 'bg-red-50 dark:bg-red-950/50 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'
                      : 'bg-muted text-foreground border border-border'
                  }`}
                >
                  {message.isError && (
                    <div className="flex items-center space-x-1 mb-1">
                      <AlertCircle className="h-3 w-3" />
                      <span className="text-xs font-medium">Error</span>
                    </div>
                  )}
                  <p className="whitespace-pre-wrap">{message.text}</p>
                  <p className="text-xs opacity-60 mt-1">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            ))}
            
            {isThinking && (
              <div className="flex justify-start animate-in slide-in-from-bottom-2 duration-300">
                <div className="bg-muted text-foreground px-3 py-2 rounded-lg border border-border">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-1.5 h-1.5 bg-foreground/60 rounded-full animate-pulse"></div>
                      <div className="w-1.5 h-1.5 bg-foreground/60 rounded-full animate-pulse delay-75"></div>
                      <div className="w-1.5 h-1.5 bg-foreground/60 rounded-full animate-pulse delay-150"></div>
                    </div>
                    <span className="text-xs text-muted-foreground">Processing your request...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <div className="p-6 border-t border-border">
            <form onSubmit={handleQuerySubmit} className="flex space-x-3">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask me about your emails, calendar, weather..."
                disabled={isThinking}
                className="flex-1 px-3 py-2 text-sm bg-background border border-border rounded-lg placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-foreground/20 focus:border-foreground transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <button
                type="submit"
                disabled={!query.trim() || isThinking}
                className="bg-foreground text-background hover:bg-foreground/90 disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed p-2 rounded-lg transition-all duration-200 transform hover:translate-y-[-1px] active:translate-y-0 disabled:transform-none"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Daily Briefing Modal */}
      {showBriefing && (
        <DailyBriefing onClose={() => setShowBriefing(false)} />
      )}

      {/* Logo Modal */}
      {showLogoModal && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center p-6 z-50 animate-in fade-in-0 duration-300">
          <div className="bg-card border border-border rounded-2xl p-8 max-w-md w-full animate-in zoom-in-95 slide-in-from-bottom-4 duration-300">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-foreground">OrbitAI Logo</h3>
              <button
                onClick={() => setShowLogoModal(false)}
                className="text-muted-foreground hover:text-foreground p-1 rounded-lg hover:bg-muted transition-colors duration-200"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="flex justify-center mb-6">
              <div 
                className="w-48 h-48 text-foreground"
                dangerouslySetInnerHTML={{ __html: orbitAISVG }}
              />
            </div>
            
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-4">
                Click the button below to download the OrbitAI logo as SVG
              </p>
              <button
                onClick={downloadSVG}
                className="flex items-center space-x-2 bg-foreground text-background hover:bg-foreground/90 font-medium py-2.5 px-4 rounded-lg transition-all duration-200 transform hover:translate-y-[-1px] active:translate-y-0 mx-auto"
              >
                <Download className="h-4 w-4" />
                <span>Download SVG</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
