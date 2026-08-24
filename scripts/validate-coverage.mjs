import { readFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

export const coveragePolicy = {
  global: { statements: 79, branches: 59 },
  critical: {
    'modulo-02-prompt-engineering/labs/06_eval_prompts_dataset.py': { statements: 87, branches: 75 },
    'modulo-03-rag/labs/_rag_common.py': { statements: 89, branches: 80 },
    'modulo-03-rag/proyecto/backend/app/rag.py': { statements: 96, branches: 83 },
    'modulo-05-harness-engineering/labs/_harness_core.py': { statements: 93, branches: 75 },
    'modulo-06-loop-engineering/labs/_loop_core.py': { statements: 85, branches: 70 },
    'modulo-07-graph-engineering/labs/_graph_core.py': { statements: 91, branches: 73 },
    'modulo-08-production-engineering/docker/app.py': { statements: 98, branches: 90 },
  },
};

function check(label, actual, minimum, failures) {
  if (!Number.isFinite(actual)) failures.push(`${label}: porcentaje ausente o inválido`);
  else if (actual + Number.EPSILON < minimum) failures.push(`${label}: ${actual.toFixed(2)}% < ${minimum.toFixed(2)}%`);
}

export function validateCoverage(report, policy = coveragePolicy) {
  if (!report || typeof report !== 'object' || !report.totals || !report.files) {
    throw new TypeError('El informe de coverage no tiene la estructura esperada.');
  }
  const failures = [];
  check('global statements', report.totals.percent_statements_covered, policy.global.statements, failures);
  check('global branches', report.totals.percent_branches_covered, policy.global.branches, failures);
  for (const [file, minimum] of Object.entries(policy.critical)) {
    const summary = report.files[file]?.summary;
    if (!summary) {
      failures.push(`${file}: falta en el informe`);
      continue;
    }
    check(`${file} statements`, summary.percent_statements_covered, minimum.statements, failures);
    check(`${file} branches`, summary.percent_branches_covered, minimum.branches, failures);
  }
  return failures;
}

async function main() {
  const reportPath = path.resolve(process.argv[2] ?? 'coverage.json');
  const report = JSON.parse(await readFile(reportPath, 'utf8'));
  const failures = validateCoverage(report);
  if (failures.length) {
    console.error(`La cobertura retrocedió (${failures.length}):\n- ${failures.join('\n- ')}`);
    process.exitCode = 1;
    return;
  }
  console.log(
    `Cobertura verificada: ${report.totals.percent_statements_covered.toFixed(2)}% statements · `
    + `${report.totals.percent_branches_covered.toFixed(2)}% branches.`,
  );
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  await main();
}
