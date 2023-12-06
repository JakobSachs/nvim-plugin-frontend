/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['../templates/*.html'],
  theme: {
    extend: {
      colors: {
        text: 'var(--text)',
        background: 'var(--background)',
        primary: 'var(--primary)',
        secondary: 'var(--secondary)',
        accent: 'var(--accent)',
      },
    },
  },
};
