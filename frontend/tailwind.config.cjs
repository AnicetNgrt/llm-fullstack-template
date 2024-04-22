/** @type {import('tailwindcss').Config}*/
const config = {
	content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}'],
  
	plugins: [
		require('flowbite/plugin'),
		require('tailwind-scrollbar')
	],
  
	darkMode: 'class',
  
	theme: {
	  extend: {
		colors: {
		  // flowbite-svelte
			primary: {
				'50': '#fdf7ef',
				'100': '#fbebd9',
				'200': '#f5d4b3',
				'300': '#efb782',
				'400': '#e79050',
				'500': '#e2732d',
				'600': '#d35b23',
				'700': '#b64820',
				'800': '#8c3820',
				'900': '#71301d',
				'950': '#3d170d',
			},
		},
		fontFamily: {
			sans: ['Satoshi', 'sans-serif'],
			mono: ['JetBrains Mono', 'monospace'],
		},
	  }
	}
  };
  
  module.exports = config;