import readline from 'node:readline';
import { c } from './style.js';

export function shouldPrompt(ctx, flags) {
  return Boolean(ctx.isTTY && !flags.yes && !flags.dryRun);
}

export function buildSkillChoices(skills) {
  return skills.map((skill) => ({
    id: skill.name,
    label: skill.name,
    hint: skill.description.slice(0, 72),
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
    lineCount: 0,
  };

  return new Promise((resolve, reject) => {
    const restore = () => {
      stdout.write('\x1b[?25h');
      if (stdin.isTTY) stdin.setRawMode(false);
      stdin.removeListener('data', onData);
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

    const draw = () => {
      if (state.lineCount) stdout.write(`\x1b[${state.lineCount}A\x1b[J`);
      const lines = [
        `${c.bold}${title}${c.reset}`,
        `${c.dim}  space toggle · ↑/↓ move · ${allKey} all · enter confirm · q quit${c.reset}`,
        '',
      ];
      state.items.forEach((item, i) => {
        const pointer = i === state.cursor ? `${c.cyan}▶${c.reset}` : ' ';
        const box = item.selected ? `${c.green}◉${c.reset}` : `${c.dim}○${c.reset}`;
        const label = i === state.cursor ? `${c.bold}${item.label}${c.reset}` : item.label;
        lines.push(` ${pointer} ${box}  ${label}  ${item.hint || ''}`);
      });
      const selected = state.items.filter((item) => item.selected).length;
      lines.push('');
      lines.push(`  ${c.dim}${selected}/${state.items.length} selected${c.reset}`);
      const text = `${lines.join('\n')}\n`;
      state.lineCount = text.split('\n').length - 1;
      stdout.write(text);
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
        return draw();
      }
      if (key === allKey || key === allKey.toUpperCase()) {
        const allOn = state.items.every((item) => item.selected);
        for (const item of state.items) item.selected = !allOn;
        return draw();
      }
      seq += key;
      if (seq.endsWith('[A') || key === 'k') {
        state.cursor = (state.cursor + state.items.length - 1) % state.items.length;
        seq = '';
        return draw();
      }
      if (seq.endsWith('[B') || key === 'j') {
        state.cursor = (state.cursor + 1) % state.items.length;
        seq = '';
        return draw();
      }
      if (seq.length > 4) seq = '';
    };

    stdout.write('\x1b[?25l');
    stdin.setRawMode(true);
    stdin.resume();
    stdin.setEncoding('utf8');
    stdin.on('data', onData);
    draw();
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

function strip(text) {
  return String(text).replace(/\x1b\[[0-9;]*m/g, '');
}
