/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    theme: {
        extend: {
            colors: {
                background: '#ffffff',
                foreground: '#000000',
                muted: '#f5f5f5',
                'muted-foreground': '#737373',
            },
        },
    },
    plugins: [],
}
