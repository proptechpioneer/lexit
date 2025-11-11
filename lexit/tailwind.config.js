/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./lexit/templates/**/*.html",
    "./lexit/**/*.py", 
    "./news/templates/**/*.html",
    "./users/templates/**/*.html",
    "./user_home/templates/**/*.html",
    "./templates/**/*.html",
    "./rra_guide/templates/**/*.html"
  ],
  theme: {
    extend: {
      colors: {
        'primary-blue': '#05113A',
        'primary-blue-force': '#05113A',
        'yellow': '#FFD700',
        'light-yellow': '#FFF5C8',
        'light-blue': '#A2CADD',
        'pink': '#E0BBFF',
        'purple': '#A084CA',
        'dark-purple': '#5A189A',
        'dark-pink': '#D94590',
        'light-grey': '#E5E3E6',
      },
      fontFamily: {
        'archivo': ['Archivo', 'sans-serif'],
        'anek-latin': ['Anek Latin', 'sans-serif'],
      },
      fontSize: {
        'h1-custom': ['96px', '88px'],
        'h2-custom': ['64px', '64px'],
        'h3-custom': ['40px', '100%'],
        'h4-custom': ['32px', '36px'],
        'h5-custom': ['20px', '24px'],
      }
    },
  },
  plugins: [],
};
