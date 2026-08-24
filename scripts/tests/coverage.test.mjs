import assert from 'node:assert/strict';
import test from 'node:test';

import { validateCoverage } from '../validate-coverage.mjs';

const policy = {
  global: { statements: 80, branches: 60 },
  critical: { 'critical.py': { statements: 90, branches: 75 } },
};

function report(globalStatements = 80, criticalBranches = 75) {
  return {
    totals: {
      percent_statements_covered: globalStatements,
      percent_branches_covered: 60,
    },
    files: {
      'critical.py': {
        summary: {
          percent_statements_covered: 90,
          percent_branches_covered: criticalBranches,
        },
      },
    },
  };
}

test('coverage policy accepts every threshold at its exact boundary', () => {
  assert.deepEqual(validateCoverage(report(), policy), []);
});

test('coverage policy reports global and critical regressions independently', () => {
  assert.deepEqual(validateCoverage(report(79.9, 74.9), policy), [
    'global statements: 79.90% < 80.00%',
    'critical.py branches: 74.90% < 75.00%',
  ]);
});

test('coverage policy fails closed when a critical file disappears', () => {
  const missing = report();
  missing.files = {};
  assert.deepEqual(validateCoverage(missing, policy), ['critical.py: falta en el informe']);
});

test('coverage policy rejects malformed reports', () => {
  assert.throws(() => validateCoverage({}, policy), /estructura esperada/);
});
