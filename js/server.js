const fastify = require('fastify')({ logger: true })
const yargs = require('yargs');
const BrowserManager = require("./browser_manager");

const argv = yargs
    .option('browser', {
      type: 'boolean',
      default: true,
    })
    .option('headless', {
      type: 'boolean',
      default: false,
    })
    .option('devtools', {
      type: 'boolean',
      default: false,
    })
    .option('slow_mo', {
        type: 'integer',
        default: 0,
    })
    .option('future', {
      type: 'boolean',
      default: true,
    })
    .option('port', {
        type: 'integer',
        default: 22000,
    })
    .argv;

(async () => {
  const browserManager = new BrowserManager(argv);
  await browserManager.init();
  fastify.get('/price', async (request, response) => {
    return await browserManager.getCurrentPrice();
  });
  fastify.get('/balance', async (request, response) => {
    return await browserManager.getCurrentBalance();
  });
  fastify.post("/fix", async(request, response) => {
    return await browserManager.fix();
  });
  fastify.post("/notouch", async(request, response) => {
    return await browserManager.noTouch();
  });
  fastify.post("/refresh", async(request, response) => {
    return await browserManager.init();
  });
  fastify.post("/reset", async(request, response) => {
    return await browserManager.resetBalance();
  });
  fastify.post("/screenshot", async(request, response) => {
    return await browserManager.screenshot();
  });
  fastify.post("/touch", async(request, response) => {
    return await browserManager.touch();
  });
  try {
    fastify.listen(argv.port);
  } catch (err) {
    fastify.log.error(err)
    process.exit(1)
  }
})();
