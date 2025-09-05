import React, { useState } from 'react';
import { Eye, EyeOff, ArrowRight, Download, X } from 'lucide-react';
import { mockAuth } from '../mock';
import { useWalkthrough } from '../contexts/WalkthroughContext';
import ThemeToggle from './ThemeToggle';

const LoginSignup = ({ setIsAuthenticated }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showLogoModal, setShowLogoModal] = useState(false);
  
  const { hasCompletedWalkthrough, startWalkthrough } = useWalkthrough();

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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (!isLogin && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    // Simulate API call with smooth loading
    setTimeout(() => {
      const result = mockAuth.authenticate(formData.email, formData.password, !isLogin);
      setIsLoading(false);
      
      if (result.success) {
        setIsAuthenticated(true);
        
        // Start walkthrough for new users (signup) or users who haven't completed it
        if (!isLogin || !hasCompletedWalkthrough) {
          setTimeout(() => {
            startWalkthrough();
          }, 1000); // Delay to let dashboard load
        }
      } else {
        setErrors({ general: result.message });
      }
    }, 800);
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setFormData({ email: '', password: '', confirmPassword: '' });
    setErrors({});
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header with theme toggle */}
      <div className="absolute top-6 right-6 z-10">
        <ThemeToggle />
      </div>

      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-sm">
          {/* Logo/Brand area */}
          <div className="text-center mb-12">
            <button 
              onClick={() => setShowLogoModal(true)}
              className="inline-flex items-center justify-center w-16 h-16 rounded-xl bg-background border border-border mb-6 transition-transform duration-200 hover:scale-105 cursor-pointer"
            >
              <img 
                src="/logo.png" 
                alt="OrbitAI Logo" 
                className="w-12 h-12 object-contain"
              />
            </button>
            <h1 className="text-2xl font-semibold text-foreground mb-2">
              {isLogin ? 'Welcome back' : 'Create your account'}
            </h1>
            <p className="text-muted-foreground text-sm">
              {isLogin ? 'Enter your credentials to continue' : 'Start your journey with us'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {errors.general && (
              <div className="p-3 text-sm text-red-600 bg-red-50 dark:bg-red-950/20 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-800/30 animate-in slide-in-from-top-1 duration-300">
                {errors.general}
              </div>
            )}

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className={`
                    w-full px-3 py-2 text-sm bg-background border rounded-lg 
                    placeholder:text-muted-foreground
                    focus:outline-none focus:ring-2 focus:ring-foreground/20 focus:border-foreground
                    transition-all duration-200
                    ${errors.email ? 'border-red-300 dark:border-red-700' : 'border-border hover:border-foreground/30'}
                  `}
                  placeholder="Enter your email"
                />
                {errors.email && (
                  <p className="text-xs text-red-600 dark:text-red-400 animate-in slide-in-from-top-1 duration-200">
                    {errors.email}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className={`
                      w-full px-3 py-2 pr-10 text-sm bg-background border rounded-lg 
                      placeholder:text-muted-foreground
                      focus:outline-none focus:ring-2 focus:ring-foreground/20 focus:border-foreground
                      transition-all duration-200
                      ${errors.password ? 'border-red-300 dark:border-red-700' : 'border-border hover:border-foreground/30'}
                    `}
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors duration-200"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-xs text-red-600 dark:text-red-400 animate-in slide-in-from-top-1 duration-200">
                    {errors.password}
                  </p>
                )}
              </div>

              {!isLogin && (
                <div className="space-y-2 animate-in slide-in-from-top-2 duration-300">
                  <label className="text-sm font-medium text-foreground">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className={`
                      w-full px-3 py-2 text-sm bg-background border rounded-lg 
                      placeholder:text-muted-foreground
                      focus:outline-none focus:ring-2 focus:ring-foreground/20 focus:border-foreground
                      transition-all duration-200
                      ${errors.confirmPassword ? 'border-red-300 dark:border-red-700' : 'border-border hover:border-foreground/30'}
                    `}
                    placeholder="Confirm your password"
                  />
                  {errors.confirmPassword && (
                    <p className="text-xs text-red-600 dark:text-red-400 animate-in slide-in-from-top-1 duration-200">
                      {errors.confirmPassword}
                    </p>
                  )}
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="
                w-full bg-foreground text-background font-medium py-2.5 px-4 rounded-lg 
                hover:bg-foreground/90 active:bg-foreground/80
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200 transform hover:translate-y-[-1px] active:translate-y-0
                disabled:transform-none
                flex items-center justify-center space-x-2
              "
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                  <span>Processing...</span>
                </div>
              ) : (
                <>
                  <span>{isLogin ? 'Sign in' : 'Create account'}</span>
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-sm text-muted-foreground">
              {isLogin ? "Don't have an account?" : "Already have an account?"}
              <button
                onClick={toggleMode}
                className="ml-1 text-foreground hover:underline font-medium transition-all duration-200"
              >
                {isLogin ? 'Sign up' : 'Sign in'}
              </button>
            </p>
          </div>
        </div>
      </div>

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

export default LoginSignup;
