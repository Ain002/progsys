import js from '@eslint/js';
import globals from 'globals';

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        // Alpine.js
        Alpine: 'readonly',
        // External libraries
        ApexCharts: 'readonly',
        Swal: 'readonly',
        bootstrap: 'readonly',
      },
    },
    rules: {
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': 'off',
      'no-case-declarations': 'off',
    },
  },
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      'dist-modern/**',
      'src/**',
      '*.min.js',
    ],
  },
];
