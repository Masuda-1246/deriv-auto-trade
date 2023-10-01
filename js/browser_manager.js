require('dotenv').config();
const DERIV = require('./deriv')
const puppeteer = require('puppeteer');

module.exports = class BrowserManager {
  constructor(argv) {
    this.browser = null;
    this.derivSession = null;
    this.argv = argv;
  }

  async init() {
    if (!this.argv.browser) {
        this.derivSession = new DERIV();
        return;
    }

    try {
      if (this.browser) {
          this.browser.close();
          this.browser = null;
      }

      this.browser = await puppeteer.launch({
          // headless: false,
          headless: this.argv.headless,
          devtools: this.argv.devtools,
          defaultViewport: {
            width: 1400,
            height: 800,
          },
          slowMo: this.argv.slowMo,
          args: [
              "--window-size=1920,1080",
              // this is for development (docker)
              // '--no-sandbox',
          ]
      });

      this.derivSession = new DERIV(this.browser, {
          email:process.env["EMAIL"],
          passwd:process.env["PASSWWORD"],
      });
      await this.derivSession.init();
      await this.derivSession.login();
      await this.derivSession.setup();
    } catch (e) {
      console.error(e);
      await this.screenshot();
      process.exit(1);
    }
    return {};
  }

  async screenshot() {
    await this.derivSession.screenshot("current-deriv");
    return {"screenshot":"Succesfully"};
  }

  async orders(param) {
    await this.derivSession.orders(param);
    return {"orders":"Succesfully"};
  }

}
