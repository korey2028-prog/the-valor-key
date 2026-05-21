/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        tiffany: '#0ABAB5',
        'tiffany-light': '#7BD5D1',
        pink_soft: '#FFD1DC',
        'pink-soft': '#FFD1DC',
        green_natural: '#7FB069',
        'green-natural': '#7FB069',
        cream: '#FFFCF6',
        'paper-gold': '#D4A373',
        'deep-blue': '#1E3A5F',
      },
      fontFamily: {
        serif: ['"Playfair Display"', '"Cormorant Garamond"', 'serif'],
        sans: ['Inter', '"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        cn: ['"Noto Serif SC"', '"PingFang SC"', 'serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.8s ease-in forwards',
        'float': 'float 6s ease-in-out infinite',
        'fade-up': 'fadeUp 1s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};
