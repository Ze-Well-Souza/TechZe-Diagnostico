
/**
 * Configurações para GitHub Actions com testes paralelos e deployment condicional
 */

export const GITHUB_WORKFLOWS = {
  ci: {
    name: 'CI Pipeline',
    on: ['push', 'pull_request'],
    jobs: {
      test_frontend: {
        name: 'Frontend Tests',
        runs_on: 'ubuntu-latest',
        strategy: {
          matrix: {
            node_version: ['18', '20'],
            store: ['ulytech', 'utilimix', 'useprint']
          }
        },
        steps: [
          'checkout',
          'setup_node',
          'install_dependencies',
          'run_linting',
          'run_unit_tests',
          'run_integration_tests',
          'upload_coverage'
        ]
      },
      test_backend: {
        name: 'Backend Tests',
        runs_on: 'ubuntu-latest',
        strategy: {
          matrix: {
            python_version: ['3.11', '3.12'],
            store: ['ulytech', 'utilimix', 'useprint']
          }
        },
        steps: [
          'checkout',
          'setup_python',
          'install_dependencies',
          'run_security_scan',
          'run_unit_tests',
          'run_integration_tests'
        ]
      },
      security_scan: {
        name: 'Security Scan',
        runs_on: 'ubuntu-latest',
        steps: [
          'checkout',
          'run_snyk_scan',
          'run_sonarqube',
          'check_dependencies'
        ]
      }
    }
  },
  
  deploy: {
    name: 'Deploy Pipeline',
    on: {
      push: {
        branches: ['main', 'staging']
      }
    },
    jobs: {
      deploy_staging: {
        name: 'Deploy to Staging',
        if: "github.ref == 'refs/heads/staging'",
        environment: 'staging',
        steps: [
          'checkout',
          'build_application',
          'deploy_to_staging',
          'run_smoke_tests'
        ]
      },
      deploy_production: {
        name: 'Deploy to Production',
        if: "github.ref == 'refs/heads/main'",
        environment: 'production',
        strategy: {
          matrix: {
            store: ['ulytech', 'utilimix', 'useprint']
          }
        },
        steps: [
          'checkout',
          'build_application',
          'deploy_canary',
          'run_health_checks',
          'promote_or_rollback'
        ]
      }
    }
  }
};

export const generateWorkflowYAML = (workflow: any): string => {
  return `
name: ${workflow.name}

on: ${JSON.stringify(workflow.on)}

jobs:
${Object.entries(workflow.jobs).map(([jobName, job]: [string, any]) => `
  ${jobName}:
    name: ${job.name}
    runs-on: ${job.runs_on}
    ${job.if ? `if: ${job.if}` : ''}
    ${job.environment ? `environment: ${job.environment}` : ''}
    ${job.strategy ? `strategy: ${JSON.stringify(job.strategy, null, 6)}` : ''}
    steps:
      ${job.steps.map((step: string) => `- name: ${step}`).join('\n      ')}
`).join('')}
`;
};
