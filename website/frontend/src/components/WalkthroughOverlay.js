import React, { useEffect, useState } from 'react';
import { X, ArrowLeft, ArrowRight } from 'lucide-react';
import { useWalkthrough } from '../contexts/WalkthroughContext';

const WalkthroughOverlay = () => {
  const { 
    isActive, 
    currentStep, 
    steps, 
    nextStep, 
    previousStep, 
    skipWalkthrough 
  } = useWalkthrough();
  
  const [targetElement, setTargetElement] = useState(null);
  const [spotlightStyle, setSpotlightStyle] = useState({});
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });

  const currentStepData = steps[currentStep];

  // OrbitAI Logo SVG (compact version)
  const orbitAILogoSVG = `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <style>
        .orbit-ring { fill: none; stroke: currentColor; stroke-width: 2.5; }
        .orbit-node { fill: currentColor; }
        .center-node { fill: currentColor; }
      </style>
    </defs>
    
    <!-- Outer Ring -->
    <circle cx="50" cy="50" r="40" class="orbit-ring"/>
    
    <!-- Inner hexagonal structure -->
    <g transform="translate(50,50)">
      <!-- Central node -->
      <circle cx="0" cy="0" r="4" class="center-node"/>
      
      <!-- Hexagon connection lines -->
      <line x1="0" y1="0" x2="0" y2="-20" class="orbit-ring"/>
      <line x1="0" y1="0" x2="17.3" y2="-10" class="orbit-ring"/>
      <line x1="0" y1="0" x2="17.3" y2="10" class="orbit-ring"/>
      <line x1="0" y1="0" x2="0" y2="20" class="orbit-ring"/>
      <line x1="0" y1="0" x2="-17.3" y2="10" class="orbit-ring"/>
      <line x1="0" y1="0" x2="-17.3" y2="-10" class="orbit-ring"/>
      
      <!-- Outer hexagon connections -->
      <line x1="0" y1="-20" x2="17.3" y2="-10" class="orbit-ring"/>
      <line x1="17.3" y1="-10" x2="17.3" y2="10" class="orbit-ring"/>
      <line x1="17.3" y1="10" x2="0" y2="20" class="orbit-ring"/>
      <line x1="0" y1="20" x2="-17.3" y2="10" class="orbit-ring"/>
      <line x1="-17.3" y1="10" x2="-17.3" y2="-10" class="orbit-ring"/>
      <line x1="-17.3" y1="-10" x2="0" y2="-20" class="orbit-ring"/>
      
      <!-- Outer nodes -->
      <circle cx="0" cy="-20" r="3" class="orbit-node"/>
      <circle cx="17.3" cy="-10" r="3" class="orbit-node"/>
      <circle cx="17.3" cy="10" r="3" class="orbit-node"/>
      <circle cx="0" cy="20" r="3" class="orbit-node"/>
      <circle cx="-17.3" cy="10" r="3" class="orbit-node"/>
      <circle cx="-17.3" cy="-10" r="3" class="orbit-node"/>
    </g>
  </svg>`;

  useEffect(() => {
    if (isActive && currentStepData?.target) {
      const element = document.querySelector(currentStepData.target);
      setTargetElement(element);
      
      if (element) {
        const rect = element.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        
        // Scroll element into view
        element.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center',
          inline: 'center' 
        });

        // Create spotlight effect (cutout for the target element)
        const padding = 8;
        const spotlightX = rect.left - padding;
        const spotlightY = rect.top - padding;
        const spotlightWidth = rect.width + (padding * 2);
        const spotlightHeight = rect.height + (padding * 2);

        setSpotlightStyle({
          clipPath: `polygon(
            0% 0%, 
            0% 100%, 
            ${spotlightX}px 100%, 
            ${spotlightX}px ${spotlightY}px, 
            ${spotlightX + spotlightWidth}px ${spotlightY}px, 
            ${spotlightX + spotlightWidth}px ${spotlightY + spotlightHeight}px, 
            ${spotlightX}px ${spotlightY + spotlightHeight}px, 
            ${spotlightX}px 100%, 
            100% 100%, 
            100% 0%
          )`
        });

        // Calculate tooltip position
        let top = rect.top + scrollTop;
        let left = rect.left + scrollLeft;
        const viewportWidth = window.innerWidth;
        const tooltipWidth = 320; // Fixed tooltip width

        switch (currentStepData.position) {
          case 'bottom':
            top = rect.bottom + scrollTop + 15;
            left = Math.max(20, Math.min(viewportWidth - tooltipWidth - 20, rect.left + scrollLeft + (rect.width / 2) - (tooltipWidth / 2)));
            break;
          case 'top':
            top = rect.top + scrollTop - 15;
            left = Math.max(20, Math.min(viewportWidth - tooltipWidth - 20, rect.left + scrollLeft + (rect.width / 2) - (tooltipWidth / 2)));
            break;
          case 'bottom-left':
            top = rect.bottom + scrollTop + 15;
            left = Math.max(20, rect.right + scrollLeft - tooltipWidth);
            break;
          case 'right':
            top = Math.max(20, rect.top + scrollTop + (rect.height / 2) - 100);
            left = Math.min(viewportWidth - tooltipWidth - 20, rect.right + scrollLeft + 15);
            break;
          default:
            top = rect.bottom + scrollTop + 15;
            left = Math.max(20, Math.min(viewportWidth - tooltipWidth - 20, rect.left + scrollLeft + (rect.width / 2) - (tooltipWidth / 2)));
        }

        setTooltipPosition({ top, left });
      }
    } else {
      setTargetElement(null);
      setSpotlightStyle({});
    }
  }, [isActive, currentStep, currentStepData]);

  if (!isActive) return null;

  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === steps.length - 1;
  const isCenterPosition = currentStepData.position === 'center' || !currentStepData.target;

  return (
    <div className="fixed inset-0 z-50">
      {/* Backdrop with spotlight cutout */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm transition-all duration-300"
        style={spotlightStyle}
      />
      
      {/* Tooltip */}
      <div
        className={`absolute bg-card border border-border rounded-xl shadow-2xl animate-in slide-in-from-bottom-4 duration-300 ${
          isCenterPosition ? 'top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 sm:w-96' : 'w-72 sm:w-80'
        }`}
        style={isCenterPosition ? {} : { 
          top: tooltipPosition.top, 
          left: tooltipPosition.left
        }}
      >
        {/* Arrow pointer for positioned tooltips */}
        {!isCenterPosition && (currentStepData.position === 'bottom' || !currentStepData.position) && (
          <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-card border-l border-t border-border rotate-45" />
        )}
        {!isCenterPosition && currentStepData.position === 'top' && (
          <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-card border-r border-b border-border rotate-45" />
        )}
        {!isCenterPosition && currentStepData.position === 'right' && (
          <div className="absolute -left-2 top-8 w-4 h-4 bg-card border-l border-b border-border rotate-45" />
        )}

        <div className="p-4 sm:p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-3 sm:mb-4">
            <div className="flex items-center space-x-2">
              <div 
                className="h-4 w-4 sm:h-5 sm:w-5 text-blue-500 flex-shrink-0"
                dangerouslySetInnerHTML={{ __html: orbitAILogoSVG }}
              />
              <h3 className="font-semibold text-foreground text-sm sm:text-base">{currentStepData.title}</h3>
            </div>
            <button
              onClick={skipWalkthrough}
              className="text-muted-foreground hover:text-foreground p-1 rounded-md hover:bg-muted transition-colors duration-200 flex-shrink-0"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Description */}
          <p className="text-muted-foreground text-xs sm:text-sm mb-4 sm:mb-6 leading-relaxed">
            {currentStepData.description}
          </p>

          {/* Progress indicator */}
          <div className="flex items-center space-x-2 mb-4 sm:mb-6">
            <div className="flex space-x-1">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={`h-1 sm:h-1.5 w-4 sm:w-6 rounded-full transition-colors duration-200 ${
                    index <= currentStep ? 'bg-blue-500' : 'bg-muted'
                  }`}
                />
              ))}
            </div>
            <span className="text-xs text-muted-foreground ml-2">
              {currentStep + 1} of {steps.length}
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <div>
              {!isFirstStep && (
                <button
                  onClick={previousStep}
                  className="flex items-center space-x-1 text-muted-foreground hover:text-foreground px-2 sm:px-3 py-1.5 rounded-md hover:bg-muted transition-all duration-200 text-xs sm:text-sm"
                >
                  <ArrowLeft className="h-3 w-3" />
                  <span>Back</span>
                </button>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={skipWalkthrough}
                className="text-xs sm:text-sm text-muted-foreground hover:text-foreground px-2 sm:px-3 py-1.5 rounded-md hover:bg-muted transition-colors duration-200"
              >
                Skip tour
              </button>
              <button
                onClick={nextStep}
                className="flex items-center space-x-1 bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm font-medium px-3 sm:px-4 py-2 rounded-md transition-all duration-200 transform hover:scale-105 active:scale-95"
              >
                <span>{isLastStep ? 'Finish' : 'Next'}</span>
                {!isLastStep && <ArrowRight className="h-3 w-3" />}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WalkthroughOverlay;
