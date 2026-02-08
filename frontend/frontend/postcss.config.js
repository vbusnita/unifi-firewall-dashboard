import tailwindcss from 'tailwindcss'
import autoprefixer from 'autoprefixer'

export default {
  plugins: [
    tailwindcss({
      content: ['**/*.{js,ts,jsx,tsx}'],
      theme: {
        colors: {
          background: '#000000',
          foreground: '#FFFFFF',
        },
      },
      plugins: [],
    }),
    autoprefixer,
  ],
}