# Contributing to the open LLM engineering curriculum

<p align="center">
  <a href="#contributing-in-english">English</a> · <a href="#contribuir-en-espanol">Español</a>
</p>

<a id="contributing-in-english"></a>

This repository is the public knowledge source for
[llmengineerclub.com](https://llmengineerclub.com). An approved and merged contribution may become
a lesson, lab, example, correction or update on the platform.

## How contributions are credited

The website preserves provenance through the merged pull request:

- **Created**: added a substantial new unit.
- **Improved**: corrected or expanded existing material with educational impact.
- **Reviewed**: gave a reasoned technical approval.
- **Maintained**: updated models, SDKs, certifications or official links.

Attribution includes the contributor's public name, username, avatar and GitHub profile, together
with the pull-request number and link. Credit is based on educational impact, not lines changed or
pull-request volume.

## Before opening a pull request

1. Explain the learning problem, who it blocks and why.
2. Link primary sources: official documentation, a paper or a standard.
3. Keep models and APIs configurable; do not introduce an obsolete model as a default.
4. Give new labs an offline or mock mode whenever reasonable.
5. Test a happy path and at least one meaningful failure.
6. Never include credentials, private prompts, personal data or customer output.
7. Run the validation commands in the README.

Pull requests containing a `solutions` folder, complete solution material or an official answer
marker are rejected automatically. Tests, rubrics, progressive hints and verifiable acceptance
criteria are welcome.

### Club Quiz proposals

You may contribute an assessable objective, base scenario, difficulty, sources and ambiguity
analysis. Never publish an active question or its exact statement, options, answer and explanation.
After merge, the editorial team produces a private variant, keeps attribution to the source pull
request and reviews it before activation. Retired questions may later be released as open practice.

The complete contract is in
[`docs/club-quiz-contributions.md`](docs/club-quiz-contributions.md).

## Repository structure

- Lessons: `modulo-NN-*/teoria/NN-title.md`.
- Labs: `modulo-NN-*/labs/NN_name.py`.
- Small fictional datasets: `modulo-NN-*/labs/data/`.
- Exercises and acceptance criteria: `ejercicios.md`. Complete solutions are private and are not
  accepted in this repository.
- Certifications: `certificaciones/<code>/`. Tasks and distractors are public; answer sheets are
  not. Coordinate reasoned keys with the maintainer outside the pull request.
- Club Quiz: contribute public blueprints under `docs/club-quiz-contributions.md`; never add the
  active question bank or its answers.
- Learning-path metadata: `course.json`.
- English editions: `translations/en/<matching-path>`, with hashes recorded in the translation
  manifest.

When translating manually, edit the matching path under `translations/en/` and record its
integrity:

```bash
node scripts/record-human-translation.mjs --path modulo-02-prompt-engineering/README.md
```

You do not need a local translation model to contribute. CI checks that code, links, Markdown
structure and Python lab ASTs remain equivalent.

The platform derives titles, routes and reading times from these conventions. Renaming a published
file changes its URL, so describe why that trade-off is worthwhile.

## Model and certification updates

An update must include:

- Exact identifier or official name.
- Status: current, legacy or historical.
- Verification date.
- Official source URL.
- Impact on labs, datasets and questions. Coordinate any answer-key change outside public history.

Automation may open a pull request, but a human expert must interpret the change before merge.

## Executable code

Public pull-request CI never receives secrets. Contributed code runs with mocks and fictional data.
Tools intended for the web product need an additional `trusted-tool` review; course snippets are not
executed directly in production.

## License and publication

By contributing, you confirm that you may publish the material under [LICENSE.md](LICENSE.md),
including its appearance on llmengineerclub.com with permanent attribution to your pull request and
public GitHub profile.

---

<a id="contribuir-en-espanol"></a>

# Contribuir al currículo abierto

Este repositorio es la fuente de conocimiento de [llmengineerclub.com](https://llmengineerclub.com).
Una contribución aprobada y fusionada puede convertirse en una lección, laboratorio, ejemplo,
corrección o actualización visible en la plataforma.

## Qué recibe reconocimiento

La web conserva la procedencia mediante la PR fusionada:

- **Creó**: añadió una unidad nueva y sustantiva.
- **Mejoró**: corrigió o amplió material existente con impacto educativo.
- **Revisó**: aprobó técnicamente el cambio con una revisión argumentada.
- **Mantuvo**: actualizó modelos, SDKs, certificaciones o enlaces oficiales.

Se muestra el nombre público, usuario, avatar y enlace al perfil de GitHub, junto con el número y
enlace de la PR. No se atribuye autoría por número de líneas ni se premia el volumen de PRs.

## Antes de abrir una PR

1. Explica el problema educativo que resuelves y a quién bloquea.
2. Enlaza fuentes primarias: documentación oficial, paper o estándar.
3. Mantén los modelos y APIs configurables; no fijes un modelo antiguo como default.
4. Si añades un lab, incluye modo offline o mock siempre que sea razonable.
5. Cubre camino feliz y al menos un error relevante.
6. Nunca incluyas claves, prompts privados, datos personales ni output de clientes.
7. Ejecuta las validaciones indicadas en el README.

Una PR que añada una carpeta `soluciones`, un solucionario completo o una implementación
marcada como respuesta oficial se rechaza automáticamente. Sí son bienvenidos los tests,
rúbricas, pistas graduales y criterios verificables que permitan aprender sin publicar la
respuesta.

### Propuestas para el Club Quiz

Puedes aportar un objetivo evaluable, un escenario base, la dificultad, fuentes y un análisis de
ambigüedad. No publiques una pregunta que ya esté activa ni su combinación exacta de enunciado,
opciones, clave y explicación. Tras el merge, el equipo editorial genera una variante privada,
conserva la atribución de la PR y la somete a revisión antes de incorporarla a D1. Las preguntas
retiradas sí pueden publicarse después como práctica abierta.

El contrato completo está en [`docs/club-quiz-contributions.md`](docs/club-quiz-contributions.md).

## Estructura

- Teoría: `modulo-NN-*/teoria/NN-titulo.md`.
- Laboratorios: `modulo-NN-*/labs/NN_nombre.py`.
- Datos pequeños y ficticios: `modulo-NN-*/labs/data/`.
- Ejercicios y criterios de aceptación: `ejercicios.md`. Las soluciones completas viven
  en un repositorio privado y **no se aceptan** en este repositorio público.
- Certificaciones: `certificaciones/<codigo>/`. Los enunciados y distractores son públicos; no
  añadas una hoja de respuestas. La clave razonada se coordina con el mantenedor fuera de la PR.
- Club Quiz: aporta blueprints públicos siguiendo `docs/club-quiz-contributions.md`; el banco activo
  y sus respuestas nunca se añaden a este repositorio.
- Metadatos de la ruta: `course.json`.
- Traducciones inglesas: `translations/en/<misma-ruta>`, con el manifiesto de hashes
  regenerado mediante `node scripts/translate-content.mjs --path <ruta>`.

Si traduces manualmente, edita la ruta equivalente en `translations/en/` y registra su integridad:

```bash
node scripts/record-human-translation.mjs --path modulo-02-prompt-engineering/README.md
```

No necesitas instalar ni usar el modelo local de traducción para contribuir. El CI comprueba que
código, enlaces, estructura Markdown y AST de los labs sigan siendo equivalentes.

La plataforma genera títulos, rutas y tiempos de lectura a partir de estas convenciones. Renombrar
un archivo publicado cambia su URL: hazlo solo cuando el beneficio compense y descríbelo en la PR.

## Actualizaciones de modelos y certificaciones

Una actualización debe incluir:

- Identificador exacto o nombre oficial.
- Estado: vigente, legacy o histórico.
- Fecha de comprobación.
- URL oficial que sustenta el cambio.
- Impacto sobre labs, datasets y preguntas; cualquier cambio de clave razonada se coordina con el
  mantenedor fuera del historial público.

Los cambios automáticos solo pueden abrir PRs. Una persona experta debe interpretarlos antes del
merge.

## Código ejecutable

El CI de una PR pública nunca recibe secretos. El código contribuido se prueba con mocks y datos
ficticios. Las herramientas que vayan a formar parte del producto web requieren revisión adicional
`trusted-tool`; ningún fragmento del curso se ejecuta directamente en Cloudflare.

## Licencia y publicación

Al contribuir confirmas que puedes aportar el material y aceptas que se publique bajo las licencias
de [LICENSE.md](LICENSE.md), incluida su aparición en llmengineerclub.com con atribución permanente
a tu PR y perfil público de GitHub.
