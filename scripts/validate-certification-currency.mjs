import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';

const course = JSON.parse(await readFile('course.json', 'utf8'));
const failures = [];

function requireValue(condition, message) {
  if (!condition) failures.push(message);
}

async function markdownCorpus(directory) {
  const files = (await readdir(directory)).filter((file) => file.endsWith('.md')).sort();
  const sources = await Promise.all(files.map(async (file) => readFile(path.join(directory, file), 'utf8')));
  return sources.join('\n');
}

const awsDirectory = 'certificaciones/aws-aif-c01';
const nvidiaDirectory = 'certificaciones/nvidia-nca-genl';
const aws = await markdownCorpus(awsDirectory);
const awsReadme = await readFile(`${awsDirectory}/README.md`, 'utf8');
const nvidiaReadme = await readFile(`${nvidiaDirectory}/README.md`, 'utf8');

const awsContract = course.certifications.find(({ code }) => code === 'AIF-C01');
requireValue(awsContract, 'Falta el contrato AIF-C01 en course.json.');
if (awsContract) {
  requireValue(awsContract.exam.durationMinutes === 90, 'AIF-C01 debe declarar 90 minutos.');
  requireValue(awsContract.exam.questions === 65, 'AIF-C01 debe declarar 65 preguntas totales.');
  requireValue(awsContract.exam.scoredQuestions === 50, 'AIF-C01 debe declarar 50 preguntas puntuables.');
  requireValue(awsContract.exam.passingScaledScore === 700, 'AIF-C01 debe declarar 700 como puntuación mínima.');
  requireValue(
    JSON.stringify(awsContract.domains.map(({ weight }) => weight)) === JSON.stringify([20, 24, 28, 14, 14]),
    'Los pesos AIF-C01 deben ser 20/24/28/14/14.',
  );
}

for (const marker of [
  'revisión **1.1**',
  '30 de abril de 2026',
  'https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01.html',
]) {
  requireValue(awsReadme.includes(marker), `El README de AIF-C01 no contiene ${marker}.`);
}

for (const concept of [
  'agentic AI',
  'Asynchronous inference',
  'Serverless inference',
  'ML tradicional',
  'context engineering',
  'token-based pricing',
  'Amazon Bedrock Prompt Management',
  'model distillation',
  'LLM-as-a-judge',
  'Amazon Quick',
  'Kiro',
  'Strands Agents',
  'Amazon Bedrock AgentCore',
  'AgentCore Identity',
  'Policy in AgentCore',
  'AWS Transform',
]) {
  requireValue(aws.toLowerCase().includes(concept.toLowerCase()), `La cobertura AIF-C01 no incluye ${concept}.`);
}

for (const retiredName of ['Amazon Forecast', 'Amazon Fraud Detector', 'AWS DeepRacer', 'Amazon QuickSight']) {
  requireValue(!aws.includes(retiredName), `La cobertura AIF-C01 conserva nomenclatura retirada: ${retiredName}.`);
}

const nvidiaContract = course.certifications.find(({ code }) => code === 'NCA-GENL');
requireValue(nvidiaContract, 'Falta el contrato NCA-GENL en course.json.');
if (nvidiaContract) {
  requireValue(nvidiaContract.exam.durationMinutes === 60, 'NCA-GENL debe declarar 60 minutos.');
  requireValue(nvidiaContract.exam.questionsMin === 50 && nvidiaContract.exam.questionsMax === 60, 'NCA-GENL debe declarar 50–60 preguntas.');
  requireValue(nvidiaContract.exam.validityYears === 2, 'NCA-GENL debe declarar dos años de validez.');
  requireValue(
    JSON.stringify(nvidiaContract.domains.map(({ weight }) => weight)) === JSON.stringify([30, 24, 22, 14, 10]),
    'Los pesos NCA-GENL deben ser 30/24/22/14/10.',
  );
}

for (const marker of [
  'https://www.nvidia.com/en-us/learn/certification/generative-ai-llm-associate/',
  'Core Machine',
  '(30%)',
  '(24%)',
  '(22%)',
  '(14%)',
  '(10%)',
]) {
  requireValue(nvidiaReadme.includes(marker), `El README de NCA-GENL no contiene ${marker}.`);
}

if (failures.length) {
  console.error(`Certificaciones desactualizadas o fuera de contrato (${failures.length}):\n- ${failures.join('\n- ')}`);
  process.exit(1);
}

console.log(`Certificaciones vigentes verificadas: AIF-C01 v1.1 (${awsContract.verifiedAt}) y NCA-GENL (${nvidiaContract.verifiedAt}).`);
