import { readdirSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import browserslist from 'browserslist';
import { defineConfig, type Plugin } from 'vite-plus';

const source = resolve(import.meta.dirname, 'apps/frontend/static_src');
const destination = resolve(import.meta.dirname, 'apps/frontend/static');

// Vite wants esbuild-style targets (e.g. `chrome153`), so convert the lowest
// browser versions of the `browserslist` in package.json. Otherwise Vite
// down-levels CSS such as `light-dark()` for its own, older default targets.
const targetNames: Record<string, string> = {
  and_chr: 'chrome',
  chrome: 'chrome',
  edge: 'edge',
  firefox: 'firefox',
  ios_saf: 'ios',
  safari: 'safari',
};
const lowestVersions: Record<string, number> = {};
browserslist().forEach((entry) => {
  const [id, version] = entry.split(' ');
  const name = targetNames[id];
  if (name) {
    lowestVersions[name] = Math.min(
      lowestVersions[name] ?? Infinity,
      parseFloat(version),
    );
  }
});
const target = Object.entries(lowestVersions).map(
  ([name, version]) => `${name}${version}`,
);

/**
 * Copies the static images to the build output, and writes a flat
 * `manifest.json` (entry name -> built file name) for django-manifest-loader.
 * Vite's own manifest is keyed by source path, which the loader can't read.
 */
const djangoManifest = (): Plugin => ({
  name: 'django-manifest',
  enforce: 'post',
  generateBundle(_options, bundle) {
    const manifest: Record<string, string> = {};
    const imagesDir = join(source, 'images');
    readdirSync(imagesDir).forEach((name) => {
      const fileName = `images/${name}`;
      this.emitFile({
        type: 'asset',
        fileName,
        source: readFileSync(join(imagesDir, name)),
      });
      manifest[fileName] = fileName;
    });

    Object.values(bundle).forEach((item) => {
      if (item.type === 'chunk') {
        if (item.isEntry) manifest[`${item.name}.js`] = item.fileName;
      } else {
        manifest[item.names[0] ?? item.fileName] = item.fileName;
      }
    });

    this.emitFile({
      type: 'asset',
      fileName: 'manifest.json',
      source: JSON.stringify(manifest, null, 2),
    });
  },
});

export default defineConfig({
  // Relative URLs, so the built CSS works wherever Django serves /static/ from.
  base: './',
  publicDir: false,
  plugins: [djangoManifest()],
  css: {
    preprocessorOptions: {
      scss: {
        // Bootstrap 5 and our own stylesheets still use `@import`.
        quietDeps: true,
        silenceDeprecations: ['import'],
      },
    },
  },
  build: {
    target,
    outDir: destination,
    emptyOutDir: true,
    assetsDir: '',
    modulePreload: false,
    rolldownOptions: {
      input: {
        blocking: join(source, 'js', 'blocking.js'),
        main: join(source, 'js', 'main.js'),
      },
      output: {
        entryFileNames: '[name]-[hash].js',
        chunkFileNames: '[name]-[hash].js',
        assetFileNames: '[name]-[hash][extname]',
      },
    },
  },
  lint: {
    env: { browser: true },
    categories: {
      correctness: 'error',
      suspicious: 'error',
      perf: 'error',
    },
    ignorePatterns: ['apps/frontend/static/**', 'cloudflare/**'],
  },
  fmt: {
    printWidth: 80,
    singleQuote: true,
    trailingComma: 'all',
    quoteProps: 'consistent',
    ignorePatterns: ['apps/frontend/static/**', '**/vendor/**', '*.html'],
  },
  test: {
    environment: 'happy-dom',
    include: ['apps/frontend/static_src/**/*.test.js'],
  },
});
