#!/usr/bin/env node

import { run, c } from './lib.js';

run(process.argv)
  .then((code) => process.exit(code ?? 0))
  .catch((err) => {
    console.error(`${c.red}${err.stack || err.message}${c.reset}`);
    process.exit(1);
  });
