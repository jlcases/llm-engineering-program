import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const defaultRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function markdownLinks(markdown) {
  return [...markdown.matchAll(/!?(?:\[[^\]]*\])\(([^)\s]+)(?:\s+"[^"]*")?\)/g)]
    .map((match) => match[1]);
}

function localTarget(root, href) {
  const withoutFragment = href.split('#', 1)[0].split('?', 1)[0];
  if (!withoutFragment || /^(?:https?:|mailto:)/i.test(withoutFragment)) return null;
  const decoded = decodeURIComponent(withoutFragment);
  if (path.isAbsolute(decoded) || decoded.split(/[\\/]/).includes('..')) {
    throw new Error(`README contiene una ruta local insegura: ${href}`);
  }
  return path.join(root, decoded);
}

function webpDimensions(image) {
  if (image.length < 30
    || image.subarray(0, 4).toString('ascii') !== 'RIFF'
    || image.subarray(8, 12).toString('ascii') !== 'WEBP') return null;

  const format = image.subarray(12, 16).toString('ascii');
  if (format === 'VP8 ') {
    if (image.subarray(23, 26).toString('hex') !== '9d012a') return null;
    return {
      width: image.readUInt16LE(26) & 0x3fff,
      height: image.readUInt16LE(28) & 0x3fff,
    };
  }
  if (format === 'VP8L') {
    if (image[20] !== 0x2f || image.length < 25) return null;
    const bits = image.readUInt32LE(21);
    return {
      width: (bits & 0x3fff) + 1,
      height: ((bits >>> 14) & 0x3fff) + 1,
    };
  }
  if (format === 'VP8X') {
    if (image.length < 30) return null;
    return {
      width: image.readUIntLE(24, 3) + 1,
      height: image.readUIntLE(27, 3) + 1,
    };
  }
  return null;
}

export async function validateRepositoryDiscovery({ root = defaultRoot } = {}) {
  const problems = [];
  const readmePath = path.join(root, 'README.md');
  const [readme, spanishCourse, englishCourse, pyproject] = await Promise.all([
    readFile(readmePath, 'utf8'),
    readFile(path.join(root, 'course.json'), 'utf8').then(JSON.parse),
    readFile(path.join(root, 'course.en.json'), 'utf8').then(JSON.parse),
    readFile(path.join(root, 'pyproject.toml'), 'utf8'),
  ]);

  const firstHeading = readme.match(/^#\s+(.+)$/m)?.[1] ?? '';
  if (!/^LLM Engineering Course:/i.test(firstHeading)) {
    problems.push('el H1 principal debe comenzar por "LLM Engineering Course:"');
  }

  const englishAnchor = readme.indexOf('id="english"');
  const spanishAnchor = readme.indexOf('id="espanol"');
  if (englishAnchor < 0 || spanishAnchor < 0 || englishAnchor >= spanishAnchor) {
    problems.push('el README debe publicar inglés primero y español después');
  }

  const searchTerms = [
    'open-source',
    'bilingual',
    'retrieval-augmented generation',
    'AI agents',
    'Model Context Protocol',
    'LLM evaluation',
    'LLMOps',
  ];
  for (const term of searchTerms) {
    if (!readme.toLocaleLowerCase('en').includes(term.toLocaleLowerCase('en'))) {
      problems.push(`falta el término descriptivo: ${term}`);
    }
  }

  const englishStart = new URL(`learn/${englishCourse.modules[0].slug}/`, englishCourse.canonicalSite).toString();
  const spanishStart = new URL(`aprender/${spanishCourse.modules[0].slug}/`, spanishCourse.canonicalSite).toString();
  const requiredCallsToAction = [
    englishCourse.canonicalSite,
    spanishCourse.canonicalSite,
    englishStart,
    spanishStart,
    new URL('quiz/', englishCourse.canonicalSite).toString(),
    new URL('live/', englishCourse.canonicalSite).toString(),
    new URL('quiz/', spanishCourse.canonicalSite).toString(),
    new URL('live/', spanishCourse.canonicalSite).toString(),
  ];
  for (const href of requiredCallsToAction) {
    if (!readme.includes(`(${href})`) && !readme.includes(`href="${href}"`)) {
      problems.push(`falta el CTA canónico: ${href}`);
    }
  }

  if (!/^description\s*=\s*"Open, bilingual LLM engineering course\b/m.test(pyproject)) {
    problems.push('pyproject.toml necesita una descripción inglesa orientada a descubrimiento');
  }

  for (const href of markdownLinks(readme)) {
    let target;
    try {
      target = localTarget(root, href);
    } catch (error) {
      problems.push(error.message);
      continue;
    }
    if (target && !(await stat(target).catch(() => null))) {
      problems.push(`enlace local inexistente: ${href}`);
    }
  }

  const heroRelative = 'docs/assets/llm-engineering-course-hero.webp';
  if (!readme.includes(heroRelative)) problems.push(`falta la cabecera visual: ${heroRelative}`);
  const hero = await readFile(path.join(root, heroRelative)).catch(() => null);
  if (!hero) {
    problems.push(`no existe la cabecera visual: ${heroRelative}`);
  } else {
    const dimensions = webpDimensions(hero);
    if (!dimensions) {
      problems.push('la cabecera visual debe ser un WebP válido');
    } else {
      const { width, height } = dimensions;
      const ratio = width / height;
      if (width < 1600 || ratio < 2.2 || ratio > 2.6) {
        problems.push(`la cabecera visual debe ser panorámica y nítida; recibida ${width}x${height}`);
      }
      if (hero.length > 256 * 1024) {
        problems.push(`la cabecera visual supera 256 KiB (${hero.length} bytes)`);
      }
    }
  }

  return problems;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const problems = await validateRepositoryDiscovery({ root: process.cwd() });
  if (problems.length) {
    console.error(`Problemas en la portada del repositorio (${problems.length}):\n- ${problems.join('\n- ')}`);
    process.exit(1);
  }
  console.log('Portada bilingüe, CTA, enlaces locales y asset social verificados.');
}
