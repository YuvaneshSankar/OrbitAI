import React, { useRef, useEffect } from 'react';
import { X, Calendar, CheckSquare, Newspaper, Lightbulb, Download, FileText } from 'lucide-react';
import { mockData } from '../mock';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const DailyBriefing = ({ onClose }) => {
  const contentRef = useRef(null);
  const scrollRef = useRef(null);

  // Auto-scroll to top when modal opens
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, []);

  const exportToPDF = async () => {
    if (!contentRef.current) return;

    try {
      // Create a temporary container with better styling for PDF
      const tempDiv = document.createElement('div');
      tempDiv.style.position = 'absolute';
      tempDiv.style.left = '-9999px';
      tempDiv.style.width = '800px';
      tempDiv.style.backgroundColor = 'white';
      tempDiv.style.padding = '40px';
      tempDiv.style.fontFamily = 'Arial, sans-serif';
      
      // Clone the content
      const clonedContent = contentRef.current.cloneNode(true);
      
      // Style the cloned content for PDF
      clonedContent.style.color = '#000';
      const sections = clonedContent.querySelectorAll('.space-y-3');
      sections.forEach(section => {
        section.style.marginBottom = '30px';
        section.style.pageBreakInside = 'avoid';
      });
      
      // Add title
      const title = document.createElement('h1');
      title.textContent = 'Daily Briefing';
      title.style.fontSize = '24px';
      title.style.fontWeight = 'bold';
      title.style.marginBottom = '30px';
      title.style.textAlign = 'center';
      title.style.color = '#000';
      
      const date = document.createElement('p');
      date.textContent = new Date().toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
      date.style.textAlign = 'center';
      date.style.marginBottom = '40px';
      date.style.color = '#666';
      
      tempDiv.appendChild(title);
      tempDiv.appendChild(date);
      tempDiv.appendChild(clonedContent);
      document.body.appendChild(tempDiv);
      
      // Generate canvas
      const canvas = await html2canvas(tempDiv, {
        backgroundColor: '#ffffff',
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
    mockData.briefing.events.forEach(event => {
      markdown += `- ${event}\n`;
    });
    markdown += `\n`;
    
    // Tasks section
    markdown += `## ✅ Priority Tasks\n\n`;
    mockData.briefing.tasks.forEach(task => {
      markdown += `- [ ] ${task}\n`;
    });
    markdown += `\n`;
    
    // News section
    markdown += `## 📰 Top News\n\n`;
    mockData.briefing.news.forEach(news => {
      markdown += `- ${news}\n`;
    });
    markdown += `\n`;
    
    // Suggestions section
    markdown += `## 💡 Suggestions\n\n`;
    mockData.briefing.suggestions.forEach(suggestion => {
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
                {mockData.briefing.events.map((event, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm text-muted-foreground animate-in slide-in-from-left-1 duration-300" style={{ animationDelay: `${index * 100}ms` }}>
                    <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 mt-2 flex-shrink-0"></div>
                    <span>{event}</span>
                  </div>
                ))}
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
                {mockData.briefing.tasks.map((task, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm text-muted-foreground animate-in slide-in-from-left-1 duration-300" style={{ animationDelay: `${index * 100 + 200}ms` }}>
                    <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 mt-2 flex-shrink-0"></div>
                    <span>{task}</span>
                  </div>
                ))}
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
                {mockData.briefing.news.map((newsItem, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm text-muted-foreground animate-in slide-in-from-left-1 duration-300" style={{ animationDelay: `${index * 100 + 400}ms` }}>
                    <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 mt-2 flex-shrink-0"></div>
                    <span>{newsItem}</span>
                  </div>
                ))}
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
                {mockData.briefing.suggestions.map((suggestion, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm text-muted-foreground animate-in slide-in-from-left-1 duration-300" style={{ animationDelay: `${index * 100 + 600}ms` }}>
                    <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 mt-2 flex-shrink-0"></div>
                    <span>{suggestion}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
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