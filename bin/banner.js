import { c } from './style.js';

const FONT = {
  ' ': ['     ', '     ', '     ', '     ', '     '],
  '-': ['     ', '     ', ' ### ', '     ', '     '],
  O: [' ### ', '#   #', '#   #', '#   #', ' ### '],
  H: ['#   #', '#   #', '#####', '#   #', '#   #'],
  M: ['#   #', '## ##', '# # #', '#   #', '#   #'],
  Y: ['#   #', '#   #', ' # # ', '  #  ', '  #  '],
  S: [' ####', '#    ', ' ### ', '    #', '#### '],
  K: ['#  # ', '# #  ', '##   ', '# #  ', '#  # '],
  I: [' ### ', '  #  ', '  #  ', '  #  ', ' ### '],
  L: ['#    ', '#    ', '#    ', '#    ', '#### '],
};

function paintWord(word, { color, scaleX = 2, on = '█' } = {}) {
  const glyphs = [...word.toUpperCase()].map((ch) => FONT[ch] || FONT[' ']);
  const rows = [];
  for (let y = 0; y < 5; y++) {
    let line = '';
    for (const glyph of glyphs) {
      for (const cell of glyph[y]) {
        line += cell === '#' ? on.repeat(scaleX) : ' '.repeat(scaleX);
      }
      line += ' ';
    }
    rows.push(`${color}${line.trimEnd()}${c.reset}`);
  }
  return rows;
}

function bar(width, ch, color) {
  return `${color}${ch.repeat(Math.max(20, width))}${c.reset}`;
}

export function renderBanner({ columns = process.stdout.columns || 80, version = '' } = {}) {
  const wide = columns >= 72;
  const scaleX = wide ? 2 : 1;
  const width = wide ? 68 : 42;
  const spark = wide
    ? [
      `${c.yellow}        ▄█▄${c.reset}`,
      `${c.yellow}      ▄█████▄${c.reset}`,
      `${c.yellow}     ██▀ █ ▀██${c.reset}`,
      `${c.yellow}      ▀█████▀${c.reset}`,
      `${c.yellow}        ▀█▀${c.reset}`,
    ]
    : [
      `${c.yellow}   ▄█▄${c.reset}`,
      `${c.yellow}  █████${c.reset}`,
      `${c.yellow}   ▀█▀${c.reset}`,
    ];

  const lines = [
    '',
    bar(width, '▄', c.dim),
    '',
    ...spark,
    '',
    ...paintWord('OH-MY', { color: c.cyan, scaleX }),
    '',
    ...paintWord('SKILLS', { color: c.green, scaleX }),
    '',
    `${c.bold}${c.yellow}  ░▒▓█ PIXEL SKILLS FOR EVERY AGENT █▓▒░${c.reset}`,
    version ? `${c.dim}  v${version}   design-preview · html-prototype${c.reset}` : '',
    '',
    bar(width, '▀', c.dim),
    '',
  ].filter((line, i, arr) => line !== '' || (arr[i - 1] !== '' && arr[i + 1] !== ''));

  return lines.join('\n');
}

export function printBanner(ctx) {
  const columns = ctx?.stdout?.columns || process.stdout.columns || 80;
  const version = ctx?.pkg?.version || '';
  const banner = renderBanner({ columns, version });
  if (ctx?.log) ctx.log(banner);
  else console.log(banner);
}
