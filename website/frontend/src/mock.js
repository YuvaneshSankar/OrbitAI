// Mock data and authentication for the SaaS application

export const mockAuth = {
  authenticate: (email, password, isSignup = false) => {
    // Simple validation - any email/password combo works
    if (email && password && password.length >= 6) {
      return {
        success: true,
        user: {
          id: '1',
          email: email,
          name: 'Yuvenesh S'
        },
        token: 'mock-jwt-token'
      };
    }
    return {
      success: false,
      message: 'Invalid credentials'
    };
  }
};

export const mockData = {
  // Chat response for RAG queries
  chatResponse: "Say what you want.",
  
  // Daily briefing data
  briefing: {
    events: [
      "Team standup at 9:00 AM",
      "Client presentation at 2:00 PM", 
      "Project review at 4:30 PM"
    ],
    tasks: [
      "Complete quarterly report",
      "Review marketing campaign",
      "Update project documentation",
      "Prepare for client meeting"
    ],
    news: [
      "Industry trends showing positive growth",
      "New technology stack released",
      "Market analysis indicates expansion opportunity"
    ],
    suggestions: [
      "Consider scheduling follow-up meetings",
      "Review and optimize current workflows",
      "Plan next quarter's objectives",
      "Update team on project milestones"
    ]
  },

  // Mock API responses
  api: {
    saveNote: (note) => {
      return {
        success: true,
        message: "Note saved successfully",
        id: Math.random().toString(36).substr(2, 9)
      };
    }
  }
};
