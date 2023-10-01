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

  fastify.post("/screenshot", async(request, response) => {
    return await browserManager.screenshot();
  });
  fastify.post("/refresh", async(request, response) => {
    return await browserManager.init();
  });
  //新規注文
  fastify.post("/orders", async(request, response) => {
    const body = request.body;
    return await browserManager.orders(body);
  });
  try {
    fastify.listen(argv.port);
  } catch (err) {
    fastify.log.error(err)
    process.exit(1)
  }
})();
