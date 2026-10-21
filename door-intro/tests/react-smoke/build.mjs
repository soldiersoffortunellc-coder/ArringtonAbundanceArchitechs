// Bundles the React smoke test. Skips quietly if esbuild/react are not installed.
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
try {
  const { build } = await import('esbuild');
  await build({
    entryPoints: [join(here, 'app.jsx')],
    outfile: join(here, 'dist/bundle.js'),
    bundle: true,
    format: 'iife',
    jsx: 'automatic',
    define: { 'process.env.NODE_ENV': '"development"' },
    logLevel: 'warning'
  });
  console.log('built tests/react-smoke/dist/bundle.js');
} catch (e) {
  if (e && e.code === 'ERR_MODULE_NOT_FOUND') console.warn('esbuild not installed; skipping React smoke bundle');
  else throw e;
}
