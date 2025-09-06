import React, { useRef, useEffect, useState } from 'react';
import { X, Calendar, CheckSquare, Newspaper, Lightbulb, Download, FileText, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

// Configure axios base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const api = axios.create({
  baseURL: API_BASE_URL,
});

const DailyBriefing = ({ onClose }) => {
  const contentRef = useRef(null);
  const scrollRef = useRef(null);
  const [briefingData, setBriefingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Auto-scroll to top when modal opens and fetch briefing data
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
    fetchBriefingData();
  }, []);

  const fetchBriefingData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching daily briefing...');
      const response = await api.get('/daily_briefing');
      
      console.log('Briefing data received:', response.data);
      setBriefingData(response.data);
      
    } catch (error) {
      console.error('Error fetching daily briefing:', error);
      
      let errorMessage = 'Failed to load daily briefing.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Please try again.';
      } else if (error.response) {
        errorMessage = `Server error (${error.response.status}): ${error.response.data?.detail || 'Please try again.'}`;
      } else if (error.request) {
        errorMessage = 'Unable to connect to the server. Please check your connection.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const exportToPDF = async () => {
    if (!contentRef.current || !briefingData) return;

    try {
      // Create a temporary container with better styling for PDF
      const tempDiv = document.createElement('div');
      tempDiv.style.position = 'absolute';
      tempDiv.style.left = '-9999px';
      tempDiv.style.width = '800px';
      tempDiv.style.backgroundColor = '#000000';
      tempDiv.style.padding = '40px';
      tempDiv.style.fontFamily = 'Arial, sans-serif';
      
      // Clone the content
      const clonedContent = contentRef.current.cloneNode(true);
      
      // Style the cloned content for PDF
      clonedContent.style.color = '#ffffff';
      const sections = clonedContent.querySelectorAll('.space-y-3');
      sections.forEach(section => {
        section.style.marginBottom = '30px';
        section.style.pageBreakInside = 'avoid';
        section.style.color = '#ffffff';
      });
      
      // Create header with logo and title
      const headerContainer = document.createElement('div');
      headerContainer.style.display = 'flex';
      headerContainer.style.flexDirection = 'column';
      headerContainer.style.alignItems = 'center';
      headerContainer.style.justifyContent = 'center';
      headerContainer.style.marginBottom = '30px';
      headerContainer.style.gap = '10px';
      
      // Add logo (PNG image) - First line
      const logoImg = document.createElement('img');
      logoImg.src = '/logo.png';
      logoImg.style.width = '48px';
      logoImg.style.height = '48px';
      logoImg.style.objectFit = 'contain';
      
      // Add title - Second line
      const title = document.createElement('h1');
      title.textContent = 'OrbitAI - Daily Briefing';
      title.style.fontSize = '24px';
      title.style.fontWeight = 'bold';
      title.style.color = '#ffffff';
      title.style.margin = '0';
      title.style.textAlign = 'center';
      
      headerContainer.appendChild(logoImg);
      headerContainer.appendChild(title);
      
      const date = document.createElement('p');
      date.textContent = new Date().toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
      date.style.textAlign = 'center';
      date.style.marginBottom = '40px';
      date.style.color = '#cccccc';
      
      tempDiv.appendChild(headerContainer);
      tempDiv.appendChild(date);
      tempDiv.appendChild(clonedContent);
      document.body.appendChild(tempDiv);
      
      // Generate canvas
      const canvas = await html2canvas(tempDiv, {
        backgroundColor: '#000000',
        scale: 2,
        logging: false,
        useCORS: true
      });
      
      // Remove temporary div
      document.body.removeChild(tempDiv);
      
      // Create PDF
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgData = canvas.toDataURL('image/png');
      const imgWidth = 210; // A4 width in mm
      const pageHeight = 295; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      let position = 0;
      
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
      
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }
      
      pdf.save(`daily-briefing-${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
    }
  };

  const exportToMarkdown = () => {
    if (!briefingData) return;
    
    const date = new Date().toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
    
    let markdown = `# Daily Briefing\n\n`;
    markdown += `**Date:** ${date}\n\n`;
    
    // Events section
    markdown += `## 📅 Today's Events\n\n`;
    briefingData.sections.events.forEach(event => {
      markdown += `- ${event}\n`;
    });
    markdown += `\n`;
    
    // Tasks section
    markdown += `## ✅ Priority Tasks\n\n`;
    briefingData.sections.tasks.forEach(task => {
      markdown += `- [ ] ${task}\n`;
    });
    markdown += `\n`;
    
    // News section
    markdown += `## 📰 Top News\n\n`;
    briefingData.sections.news.forEach(news => {
      markdown += `- ${news}\n`;
    });
    markdown += `\n`;
    
    // Suggestions section
    markdown += `## 💡 Suggestions\n\n`;
    briefingData.sections.suggestions.forEach(suggestion => {
      markdown += `- ${suggestion}\n`;
    });
    markdown += `\n`;
    
    // Create and download file
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `daily-briefing-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-200">
      <div className="bg-card border border-border rounded-xl w-full max-w-2xl max-h-[85vh] overflow-hidden shadow-lg animate-in slide-in-from-bottom-4 duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div>
            <h2 className="text-xl font-semibold text-foreground">Daily Briefing</h2>
            <p className="text-sm text-muted-foreground mt-1">Your personalized overview for today</p>
          </div>
          <div className="flex items-center space-x-2">
            {/* Export buttons */}
            <div className="flex items-center space-x-1 bg-muted rounded-lg p-1">
              <button
                onClick={exportToPDF}
                className="flex items-center space-x-1 px-2 py-1.5 rounded-md text-xs font-medium text-foreground hover:bg-background transition-colors duration-200"
                title="Export as PDF"
              >
                <Download className="h-3 w-3" />
                <span className="hidden sm:inline">PDF</span>
              </button>
              <button
                onClick={exportToMarkdown}
                className="flex items-center space-x-1 px-2 py-1.5 rounded-md text-xs font-medium text-foreground hover:bg-background transition-colors duration-200"
                title="Export as Markdown"
              >
                <FileText className="h-3 w-3" />
                <span className="hidden sm:inline">MD</span>
              </button>
            </div>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground p-1.5 rounded-lg hover:bg-muted transition-all duration-200"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div 
          ref={scrollRef}
          className="overflow-y-auto max-h-[calc(85vh-140px)] scroll-smooth" 
          style={{ scrollBehavior: 'smooth' }}
        >
          {loading ? (
            <div className="flex items-center justify-center p-12">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin mx-auto text-foreground mb-4" />
                <p className="text-foreground font-medium">Loading your daily briefing...</p>
                <p className="text-xs text-muted-foreground mt-2">This may take a moment if generating new content</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center p-12">
              <div className="text-center">
                <AlertCircle className="h-8 w-8 mx-auto text-red-500 mb-4" />
                <p className="text-foreground font-medium mb-2">Failed to load briefing</p>
                <p className="text-xs text-muted-foreground mb-4">{error}</p>
                <button
                  onClick={fetchBriefingData}
                  className="bg-foreground text-background hover:bg-foreground/90 font-medium py-2 px-4 rounded-lg transition-all duration-200"
                >
                  Try Again
                </button>
              </div>
            </div>
          ) : (
            <div ref={contentRef} className="p-6 space-y-6">
              {/* Events Section */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
                    <Calendar className="h-4 w-4 text-foreground" />
                  </div>
                  <h3 className="font-medium text-foreground">Today's Events</h3>
                </div>
                <div className="ml-10 space-y-2">
                  {briefingData?.sections?.events?.length > 0 ? (
                    briefingData.sections.events.map((event, index) => (
                      <div key={index} className="flex items-start space-x-2 text-sm text-muted-foreground animate-in slide-in-from-left-1 duration-300" style={{ animationDelay: `${index * 100}ms` }}>
                        <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 mt-2 flex-shrink-0"></div>
                        <span>{event}</span>
                      </div>
                    ))
                  ) : (
                    <div className="ml-4 text-sm text-muted-foreground">
                      <span>No events scheduled for today</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Tasks Section */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
                    <CheckSquare className="h-4 w-4 text-foreground" />
                  </div>
                  <h3 className="font-medium text-foreground">Priority Tasks</h3>
                </div>
                <div className="ml-10 space-y-2">
                  {briefingData?.sections?.tasks?.length > 0 ? (
                    briefingData.sections.tasks.map((task, index) => (
                      <div key={index} className="flex items-start space-x-2 text-sm text-muted-foreground animate-in slide-in-from-left-1 duration-300" style={{ animationDelay: `${index * 100 + 200}ms` }}>
                        <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 mt-2 flex-shrink-0"></div>
                        <span>{task}</span>
                      </div>
                    ))
                  ) : (
                    <div className="ml-4 text-sm text-muted-foreground">
                      <span>No priority tasks for today</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Top News Section */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
                    <Newspaper className="h-4 w-4 text-foreground" />
                  </div>
                  <h3 className="font-medium text-foreground">Top News</h3>
                </div>
                <div className="ml-10 space-y-2">
                  {briefingData?.sections?.news?.length > 0 ? (
                    briefingData.sections.news.map((newsItem, index) => (
                      <div key={index} className="flex items-start space-x-2 text-sm text-muted-foreground animate-in slide-in-from-left-1 duration-300" style={{ animationDelay: `${index * 100 + 400}ms` }}>
                        <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 mt-2 flex-shrink-0"></div>
                        <span>{newsItem}</span>
                      </div>
                    ))
                  ) : (
                    <div className="ml-4 text-sm text-muted-foreground">
                      <span>No news available</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Suggestions Section */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
                    <Lightbulb className="h-4 w-4 text-foreground" />
                  </div>
                  <h3 className="font-medium text-foreground">Suggestions</h3>
                </div>
                <div className="ml-10 space-y-2">
                  {briefingData?.sections?.suggestions?.length > 0 ? (
                    briefingData.sections.suggestions.map((suggestion, index) => (
                      <div key={index} className="flex items-start space-x-2 text-sm text-muted-foreground animate-in slide-in-from-left-1 duration-300" style={{ animationDelay: `${index * 100 + 600}ms` }}>
                        <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 mt-2 flex-shrink-0"></div>
                        <span>{suggestion}</span>
                      </div>
                    ))
                  ) : (
                    <div className="ml-4 text-sm text-muted-foreground">
                      <span>No suggestions available</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-border">
          <button
            onClick={onClose}
            className="w-full bg-foreground text-background hover:bg-foreground/90 font-medium py-2.5 px-4 rounded-lg transition-all duration-200 transform hover:translate-y-[-1px] active:translate-y-0"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default DailyBriefing;
