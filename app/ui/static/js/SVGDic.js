console.log('[DEBUG] SVGDic.js loaded');
const GH_DIAGRAMS = {
    polytunnel: `<svg viewBox="0 0 200 150" fill="none" xmlns="http://www.w3.org/2000/svg">
        
        <rect x="30" y="20" width="140" height="110" rx="50" stroke="rgba(27,48,34,0.1)" stroke-width="1.5" fill="rgba(27,48,34,0.02)"/>
        <rect x="90" y="25" width="20" height="100" fill="rgba(27,48,34,0.03)" stroke="rgba(27,48,34,0.1)" stroke-width="0.5"/>
        <rect x="40" y="30" width="45" height="40" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="40" y="80" width="45" height="40" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="115" y="30" width="45" height="40" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="115" y="80" width="45" height="40" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <line x1="100" y1="145" x2="100" y2="135" stroke="#A67C27" stroke-width="1.5" marker-end="url(#arrowY)"/>
        <text x="100" y="150" fill="#A67C27" font-size="7" text-anchor="middle" font-family="Inter">☀ SOUTH</text>
        <defs><marker id="arrowY" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto"><path d="M0,6 L3,0 L6,6" fill="#A67C27"/></marker></defs>
    </svg>`,
    polycarbonate: `<svg viewBox="0 0 200 150" fill="none" xmlns="http://www.w3.org/2000/svg">
        
        <rect x="25" y="20" width="150" height="110" stroke="rgba(27,48,34,0.1)" stroke-width="1.5" fill="rgba(27,48,34,0.02)" rx="3"/>
        <line x1="100" y1="20" x2="100" y2="130" stroke="rgba(27,48,34,0.05)" stroke-width="0.8" stroke-dasharray="4,3"/>
        <rect x="90" y="22" width="20" height="106" fill="rgba(27,48,34,0.03)" stroke="rgba(27,48,34,0.08)" stroke-width="0.5"/>
        <rect x="32" y="28" width="52" height="30" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="32" y="64" width="52" height="30" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="32" y="96" width="52" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="116" y="28" width="52" height="30" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="116" y="64" width="52" height="30" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="116" y="96" width="52" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="92" y="125" width="16" height="7" fill="rgba(166,124,39,0.1)" stroke="#A67C27" stroke-width="0.8" rx="1"/>
        <text x="100" y="150" fill="#A67C27" font-size="7" text-anchor="middle" font-family="Inter">☀ SOUTH</text>
    </svg>`,
    passive_solar: `<svg viewBox="0 0 200 150" fill="none" xmlns="http://www.w3.org/2000/svg">
        
        <rect x="25" y="20" width="150" height="110" stroke="rgba(27,48,34,0.1)" stroke-width="1.5" fill="rgba(27,48,34,0.02)" rx="3"/>
        <rect x="25" y="20" width="150" height="12" fill="rgba(27,48,34,0.05)" stroke="rgba(27,48,34,0.1)" stroke-width="1"/>
        <text x="100" y="29" fill="rgba(27,48,34,0.5)" font-size="6" text-anchor="middle" font-family="Inter">INSULATED NORTH WALL</text>
        <rect x="25" y="125" width="150" height="5" fill="rgba(255,214,10,0.2)" stroke="#A67C27" stroke-width="0.8"/>
        <circle cx="40" cy="45" r="6" fill="rgba(244,163,0,0.2)" stroke="rgba(244,163,0,0.4)" stroke-width="0.8"/>
        <circle cx="160" cy="45" r="6" fill="rgba(244,163,0,0.2)" stroke="rgba(244,163,0,0.4)" stroke-width="0.8"/>
        <text x="100" y="47" fill="rgba(244,163,0,0.5)" font-size="5" text-anchor="middle" font-family="Inter">THERMAL MASS</text>
        <rect x="35" y="55" width="55" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="35" y="90" width="55" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="110" y="55" width="55" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="110" y="90" width="55" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="93" y="38" width="14" height="84" fill="rgba(27,48,34,0.02)" stroke="rgba(27,48,34,0.05)" stroke-width="0.5"/>
        <text x="100" y="150" fill="#A67C27" font-size="7" text-anchor="middle" font-family="Inter">☀ SOUTH-FACING GLAZING</text>
    </svg>`,
};
