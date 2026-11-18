// Performance measurements are advisory until an owner-approved baseline is recorded.
// Fail on audit execution errors, never silently invent an SEO/performance PASS.
const profile = process.env.SEFA_LH_PROFILE || 'mobile';
if (!['mobile', 'desktop'].includes(profile)) throw new Error('Unknown Lighthouse profile');
module.exports = {
  ci: {
    collect: {
      staticDistDir: '.',
      url: ['http://localhost/index.html'],
      numberOfRuns: 1,
      settings: {
        ...(profile === 'desktop' ? {preset:'desktop'} : {}),
        chromeFlags: '--headless --no-sandbox --disable-gpu'
      }
    }
  }
};
