export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: { panel: 'rgba(15, 23, 42, 0.72)' },
      boxShadow: { glow: '0 0 40px rgba(56, 189, 248, 0.18)' }
    }
  },
  plugins: []
};
