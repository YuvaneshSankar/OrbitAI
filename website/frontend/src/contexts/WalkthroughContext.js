import React, { createContext, useContext, useState } from 'react';

const WalkthroughContext = createContext();

export const useWalkthrough = () => {
  const context = useContext(WalkthroughContext);
  if (!context) {
    throw new Error('useWalkthrough must be used within a WalkthroughProvider');
  }
  return context;
};

export const WalkthroughProvider = ({ children }) => {
  const [isActive, setIsActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [hasCompletedWalkthrough, setHasCompletedWalkthrough] = useState(
    localStorage.getItem('walkthrough_completed') === 'true'
  );

  const steps = [
    {
      id: 'welcome',
      title: 'Welcome to your Dashboard!',
      description: 'Let\'s take a quick tour of your new workspace. This will only take a minute.',
      target: null,
      position: 'center'
    },
    {
      id: 'daily-briefing',
      title: 'Daily Briefing',
      description: 'Start your day right! Click here to get your personalized overview of events, tasks, news, and suggestions.',
      target: '[data-tour="daily-briefing"]',
      position: 'bottom'
    },
    {
      id: 'quick-notes',
      title: 'Quick Notes',
      description: 'Capture your thoughts instantly. Add notes or tasks that will be saved for later.',
      target: '[data-tour="quick-notes"]',
      position: 'bottom'
    },
    {
      id: 'ai-assistant',
      title: 'AI Assistant',
      description: 'Ask anything you need help with. Your personal assistant is ready to help with questions and tasks.',
      target: '[data-tour="ai-assistant"]',
      position: 'top'
    },
    {
      id: 'theme-toggle',
      title: 'Customize Your Experience',
      description: 'Switch between light, dark, or system themes to match your preference.',
      target: '[data-tour="theme-toggle"]',
      position: 'right'
    },
    {
      id: 'complete',
      title: 'You\'re All Set!',
      description: 'You\'re ready to be productive! You can always restart this tour by clicking the help button in the header.',
      target: null,
      position: 'center'
    }
  ];

  const startWalkthrough = () => {
    setIsActive(true);
    setCurrentStep(0);
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      completeWalkthrough();
    }
  };

  const previousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const skipWalkthrough = () => {
    completeWalkthrough();
  };

  const completeWalkthrough = () => {
    setIsActive(false);
    setCurrentStep(0);
    setHasCompletedWalkthrough(true);
    localStorage.setItem('walkthrough_completed', 'true');
  };

  const restartWalkthrough = () => {
    setHasCompletedWalkthrough(false);
    localStorage.removeItem('walkthrough_completed');
    startWalkthrough();
  };

  const value = {
    isActive,
    currentStep,
    steps,
    hasCompletedWalkthrough,
    startWalkthrough,
    nextStep,
    previousStep,
    skipWalkthrough,
    completeWalkthrough,
    restartWalkthrough
  };

  return (
    <WalkthroughContext.Provider value={value}>
      {children}
    </WalkthroughContext.Provider>
  );
};