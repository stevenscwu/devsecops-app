// eslint.config.js (no require, pure ESM-compatible)

import pluginTs from '@typescript-eslint/eslint-plugin';
import parserTs from '@typescript-eslint/parser';

/** @type {import("eslint").Linter.FlatConfig[]} */
export default [
  {
    files: ['src/**/*.ts'],
    languageOptions: {
      parser: parserTs,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        project: ['./tsconfig.json'],
        tsconfigRootDir: new URL('.', import.meta.url).pathname
      }
    },
    plugins: {
      '@typescript-eslint': pluginTs
    },
    rules: {
      'no-console': 'warn',
      'no-eval': 'error',
      '@typescript-eslint/no-unused-vars': 'warn'
    }
  }
];
