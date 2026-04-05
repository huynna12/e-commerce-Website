import React, { useRef, useEffect } from 'react';
import gsap from 'gsap';

const LoadingIndicator = ({ 
  size = 'medium',
  showText = true,
  text = 'Loading...'
}) => {
  const spinnerRef = useRef(null);
  const containerRef = useRef(null);
  
  useEffect(() => {
    // Create smooth rotating animation with subtle scale pulse
    const tl = gsap.timeline();
    
    tl.to(spinnerRef.current, {
      rotation: 360,
      duration: 1.2,
      repeat: -1,
      ease: "linear"
    })
    .to(spinnerRef.current, {
      scale: 1.05,
      duration: 0.8,
      repeat: -1,
      yoyo: true,
      ease: "power2.inOut"
    }, 0);

    // Fade in entrance
    gsap.fromTo(containerRef.current, 
      { opacity: 0, y: 5 },
      { opacity: 1, y: 0, duration: 0.3 }
    );
    
    return () => {
      gsap.killTweensOf([spinnerRef.current, containerRef.current]);
    };
  }, []);

  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-6 h-6', 
    large: 'w-8 h-8'
  };
  
  return (
    <div 
      ref={containerRef}
      className="flex items-center justify-center gap-3 p-4"
    >
      <div 
        ref={spinnerRef} 
        className={`
          ${sizeClasses[size]}
          border-2 border-blue-200 border-t-blue-500 
          rounded-full shadow-sm
        `}
      />
      {showText && (
        <p className="text-gray-600 font-medium tracking-wide">
          {text}
        </p>
      )}
    </div>
  );
};

export default LoadingIndicator;