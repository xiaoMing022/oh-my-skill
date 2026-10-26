import readline from 'node:readline';
import { c } from './style.js';

export function shouldPrompt(ctx, flags) {
  return Boolean(ctx.isTTY && !flags.yes && !flags.dryRun);
}

export function buildSkillChoices(skills) {
  return skills.map((skill) => ({
    id: skill.name,
    label: skill.name,
    hint: skill.description,
    selected: true,
  }));
}

export async function promptMultiSelect(ctx, { title, items, allKey = 'a' }) {
  if (!items.length) return [];
  if (!ctx.stdin?.isTTY || typeof ctx.stdin.setRawMode !== 'function') {
    return promptByLine(ctx, { title, items });
  }
  try {
    return await promptRaw(ctx, { title, items, allKey });
  } catch (err) {
    if (err?.code === 'CANCELED') throw err;
    return promptByLine(ctx, { title, items });
  }
}

async function promptByLine(ctx, { title, items }) {
  const stdout = ctx.stdout || process.stdout;
  const stdin = ctx.stdin || process.stdin;
  stdout.write(`\n${title}\n`);
  items.forEach((item, i) => {
    const mark = item.selected ? 'x' : ' ';
    stdout.write(`  [${mark}] ${i + 1}) ${strip(item.label)}  ${strip(item.hint || '')}\n`);
  });
  stdout.write('  Numbers (1,3), "detected"/"selected", "all", or empty to keep marks: ');

  const answer = await readLine(stdin, stdout);
  const text = answer.trim().toLowerCase();
  if (text === 'q' || text === 'quit') {
    throw Object.assign(new Error('canceled'), { code: 'CANCELED' });
  }
  if (text === 'all' || text === '*') return items.map((item) => item.id);
  if (text === '' || text === 'detected' || text === 'selected') {
    return items.filter((item) => item.selected).map((item) => item.id);
  }
  const picked = new Set();
  for (const part of text.split(/[,\s]+/)) {
    const n = Number(part);
    if (Number.isInteger(n) && items[n - 1]) picked.add(items[n - 1].id);
    else if (items.some((item) => item.id === part)) picked.add(part);
  }
  return [...picked];
}

function promptRaw(ctx, { title, items, allKey }) {
  const stdin = ctx.stdin;
  const stdout = ctx.stdout || process.stdout;
  const state = {
    cursor: 0,
    items: items.map((item) => ({ ...item })),
    listLineCount: 0,
  };

  return new Promise((resolve, reject) => {
    const restore = () => {
      stdout.write('\x1b[?25h');
      if (stdin.isTTY) stdin.setRawMode(false);
      stdin.removeListener('data', onData);
      if (typeof stdout.removeListener === 'function') stdout.removeListener('resize', onResize);
      stdin.pause();
    };

    const finish = (ids) => {
      restore();
      resolve(ids);
    };

    const cancel = () => {
      restore();
      stdout.write(`\n${c.yellow}Canceled.${c.reset}\n`);
      reject(Object.assign(new Error('canceled'), { code: 'CANCELED' }));
    };

    // One spare column: writing into the last column makes some terminals wrap early.
    const columns = () => Math.max(40, (Number(stdout.columns) || 80) - 1);

    const drawList = () => {
      if (state.listLineCount > 0) {
        stdout.write(`\r\x1b[${state.listLineCount}A\x1b[J`);
      }

      const width = columns();
      const listLines = [];
      state.items.forEach((item, i) => {
        const pointer = i === state.cursor ? `${c.cyan}▶${c.reset}` : ' ';
        const box = item.selected ? `${c.green}◉${c.reset}` : `${c.dim}○${c.reset}`;
        const label = i === state.cursor ? `${c.bold}${item.label}${c.reset}` : item.label;
        const prefix = ` ${pointer} ${box}  ${label}`;
        const prefixWidth = visibleWidth(prefix);
        const room = Math.max(0, width - prefixWidth - 2);
        const hint = room > 8 ? `  ${c.dim}${truncatePlain(item.hint || '', room)}${c.reset}` : '';
        listLines.push(fitPlainWidth(`${prefix}${hint}`, width));
      });
      const selected = state.items.filter((item) => item.selected).length;
      listLines.push('');
      listLines.push(fitPlainWidth(`  ${c.dim}${selected}/${state.items.length} selected${c.reset}`, width));

      state.listLineCount = listLines.length;
      stdout.write(`${listLines.map((line) => `\x1b[2K${line}`).join('\n')}\n`);
    };

    const onResize = () => {
      // Old rows may have re-wrapped at the new width, so clear from the title down.
      stdout.write('\x1b[2J\x1b[H');
      writeHeader();
      state.listLineCount = 0;
      drawList();
    };

    let seq = '';
    const onData = (chunk) => {
      const key = String(chunk);
      if (key === '\x03') return cancel();
      if (key === 'q' || key === 'Q') return cancel();
      if (key === '\r' || key === '\n') {
        return finish(state.items.filter((item) => item.selected).map((item) => item.id));
      }
      if (key === ' ') {
        state.items[state.cursor].selected = !state.items[state.cursor].selected;
        return drawList();
      }
      if (key === allKey || key === allKey.toUpperCase()) {
        const allOn = state.items.every((item) => item.selected);
        for (const item of state.items) item.selected = !allOn;
        return drawList();
      }
      seq += key;
      if (seq.endsWith('[A') || key === 'k') {
        state.cursor = (state.cursor + state.items.length - 1) % state.items.length;
        seq = '';
        return drawList();
      }
      if (seq.endsWith('[B') || key === 'j') {
        state.cursor = (state.cursor + 1) % state.items.length;
        seq = '';
        return drawList();
      }
      if (seq.length > 4) seq = '';
    };

    const writeHeader = () => {
      stdout.write(`\n${c.bold}${title}${c.reset}\n`);
      stdout.write(`${c.dim}  space toggle · ↑/↓ move · ${allKey} all · enter confirm · q quit${c.reset}\n\n`);
    };

    stdout.write('\x1b[?25l');
    writeHeader();
    stdin.setRawMode(true);
    stdin.resume();
    stdin.setEncoding('utf8');
    stdin.on('data', onData);
    if (typeof stdout.on === 'function') stdout.on('resize', onResize);
    drawList();
  });
}

function readLine(stdin, stdout) {
  const rl = readline.createInterface({ input: stdin, output: stdout, terminal: Boolean(stdin.isTTY) });
  return new Promise((resolve) => {
    rl.once('line', (line) => {
      rl.close();
      resolve(line);
    });
  });
}

export function strip(text) {
  return String(text).replace(/\x1b\[[0-9;]*m/g, '');
}

/** Terminal column width of one code point: 0 for combining marks, 2 for East Asian wide / emoji. */
export function charWidth(cp) {
  if (cp < 32 || (cp >= 0x7f && cp < 0xa0)) return 0;
  if (
    (cp >= 0x0300 && cp <= 0x036f) ||
    (cp >= 0x200b && cp <= 0x200f) ||
    (cp >= 0xfe00 && cp <= 0xfe0f)
  ) return 0;
  if (
    (cp >= 0x1100 && cp <= 0x115f) ||
    (cp >= 0x2e80 && cp <= 0x303e) ||
    (cp >= 0x3041 && cp <= 0x33ff) ||
    (cp >= 0x3400 && cp <= 0x4dbf) ||
    (cp >= 0x4e00 && cp <= 0x9fff) ||
    (cp >= 0xa000 && cp <= 0xa4cf) ||
    (cp >= 0xac00 && cp <= 0xd7a3) ||
    (cp >= 0xf900 && cp <= 0xfaff) ||
    (cp >= 0xfe30 && cp <= 0xfe4f) ||
    (cp >= 0xff00 && cp <= 0xff60) ||
    (cp >= 0xffe0 && cp <= 0xffe6) ||
    (cp >= 0x1f300 && cp <= 0x1f64f) ||
    (cp >= 0x1f900 && cp <= 0x1f9ff) ||
    (cp >= 0x20000 && cp <= 0x3fffd)
  ) return 2;
  return 1;
}

export function visibleWidth(text) {
  let width = 0;
  for (const ch of strip(text)) width += charWidth(ch.codePointAt(0));
  return width;
}

export function truncatePlain(text, max) {
  const value = String(text || '').replace(/\s+/g, ' ').trim();
  if (max <= 0) return '';
  if (visibleWidth(value) <= max) return value;
  if (max <= 1) return '…';
  let out = '';
  let width = 0;
  for (const ch of value) {
    const w = charWidth(ch.codePointAt(0));
    if (width + w > max - 1) break;
    out += ch;
    width += w;
  }
  return `${out}…`;
}

/** Keep a single terminal row: truncate plain content if wider than columns. */
export function fitPlainWidth(text, width) {
  if (visibleWidth(text) <= width) return text;
  return truncatePlain(strip(text), width);
}
