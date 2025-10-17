import React, { useState } from 'react';

const RippleButton = ({ 
  children, 
  onClick, 
  className = '', 
  variant = 'primary',
  disabled = false,
  type = 'button',
  ariaLabel,
  ...props 
}) => {
  const [ripples, setRipples] = useState([]);

  const addRipple = (event) => {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    const newRipple = {
      x,
      y,
      size,
      id: Date.now()
    };

    setRipples([...ripples, newRipple]);

    // Remove ripple after animation
    setTimeout(() => {
      setRipples((prevRipples) => prevRipples.filter(r => r.id !== newRipple.id));
    }, 600);

    // Call original onClick
    if (onClick && !disabled) {
      onClick(event);
    }
  };

  const baseStyles = `
    relative overflow-hidden touch-manipulation 
    transform active:scale-95 transition-all duration-200
    flex flex-row items-center justify-center whitespace-nowrap
    ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
  `;

  const variantStyles = {
    primary: 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 active:from-blue-800 active:to-purple-800 text-white font-bold px-6 py-4 rounded-xl shadow-lg hover:shadow-xl active:shadow-md min-h-[56px] gap-2',
    secondary: 'bg-white hover:bg-gray-50 active:bg-gray-100 border-2 border-gray-300 hover:border-gray-400 text-gray-800 font-bold px-6 py-4 rounded-xl shadow-md hover:shadow-lg active:shadow-sm min-h-[56px] gap-2',
    pill: 'px-6 py-3 bg-gray-50 active:bg-blue-50 border-2 border-gray-200 active:border-blue-400 rounded-full text-sm font-semibold text-gray-700 active:text-blue-700 transition-all duration-100 min-h-[48px] gap-2',
    icon: 'w-10 h-10 rounded-full bg-gray-800 hover:bg-blue-600 active:bg-blue-700 flex items-center justify-center'
  };

  return (
    <button
      type={type}
      onClick={addRipple}
      disabled={disabled}
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      aria-label={ariaLabel}
      {...props}
    >
      {/* Content - removed wrapper to allow proper flex alignment */}
      {children}

      {/* Ripple Effects */}
      {ripples.map((ripple) => (
        <span
          key={ripple.id}
          className="absolute bg-white/30 rounded-full pointer-events-none animate-ripple"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: ripple.size,
            height: ripple.size,
          }}
        />
      ))}
    </button>
  );
};

export default RippleButton;
