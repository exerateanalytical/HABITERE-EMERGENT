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
    transform active:scale-95 transition-transform duration-100
    ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
  `;

  const variantStyles = {
    primary: 'bg-gradient-to-r from-blue-600 to-purple-600 active:from-blue-700 active:to-purple-700 text-white font-bold px-8 py-5 rounded-2xl shadow-lg active:shadow-md min-h-[56px]',
    secondary: 'bg-white active:bg-gray-100 border-2 border-gray-300 text-gray-800 font-bold px-8 py-5 rounded-2xl shadow-md active:shadow-sm min-h-[56px]',
    pill: 'px-6 py-3 bg-gray-50 active:bg-blue-50 border-2 border-gray-200 active:border-blue-400 rounded-full text-sm font-semibold min-h-[48px]',
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
      {/* Content */}
      <span className="relative z-10">{children}</span>

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
