
/**
 * Configurações padronizadas de ESLint e Prettier
 */

export const ESLINT_CONFIG = {
  extends: [
    '@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:security/recommended',
    'prettier'
  ],
  plugins: [
    '@typescript-eslint',
    'react',
    'react-hooks',
    'security',
    'import'
  ],
  rules: {
    // TypeScript específicas
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    '@typescript-eslint/no-explicit-any': 'warn',
    
    // React específicas
    'react/prop-types': 'off',
    'react/react-in-jsx-scope': 'off',
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    
    // Segurança
    'security/detect-object-injection': 'error',
    'security/detect-sql-injection': 'error',
    'security/detect-xss': 'error',
    
    // Importações
    'import/order': ['error', {
      'groups': [
        'builtin',
        'external',
        'internal',
        'parent',
        'sibling',
        'index'
      ],
      'newlines-between': 'always'
    }],
    
    // Multi-tenancy específicas
    'no-hardcoded-credentials': 'error',
    'tenant-isolation': 'error'
  },
  overrides: [
    {
      files: ['**/*.test.ts', '**/*.test.tsx'],
      env: {
        jest: true
      },
      rules: {
        '@typescript-eslint/no-explicit-any': 'off'
      }
    }
  ]
};

export const PRETTIER_CONFIG = {
  semi: true,
  trailingComma: 'es5' as const,
  singleQuote: true,
  printWidth: 100,
  tabWidth: 2,
  useTabs: false,
  bracketSpacing: true,
  arrowParens: 'avoid' as const,
  endOfLine: 'lf' as const
};

export const PYTHON_FLAKE8_CONFIG = {
  max_line_length: 100,
  extend_ignore: ['E203', 'W503'],
  exclude: [
    '.git',
    '__pycache__',
    'build',
    'dist',
    '.venv'
  ],
  per_file_ignores: {
    '__init__.py': 'F401'
  }
};
