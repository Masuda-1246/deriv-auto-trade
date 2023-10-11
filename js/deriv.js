const format = require("date-fns/format");
const slack = require("./slack");
module.exports = class DERIV {
  constructor (browser, credantial) {
    this.browser  = browser;
    this.credantial = credantial;
    this.url = 'https://app.deriv.com/appstore/traders-hub'
  }

  async init() {
    this.page = await this.browser.newPage();
    await this.page.goto(this.url);
  }


  //ログイン処理
  async login() {
    try {
      await this.page.waitForSelector('#txtEmail');
      //ログインIDを入力
      await this.page.type('#txtEmail', this.credantial.email)
      //パスワードを入力
      await this.page.type('#txtPass', this.credantial.passwd)
      //ログインボタン押下
      await this.page.click('button[type="submit"]')
      await this.page.waitForNavigation()
    } catch (e) {
      console.log(e.message)
    }
  }

  async changeAccount() {
    //  Demo Account切り替え
    await this.page.waitForSelector(".ic-icon.ic-1HZ100V")

    await this.page.waitForSelector("#dt_core_account-info_acc-info")
    await this.page.click("#dt_core_account-info_acc-info")
    await this.page.waitForTimeout(300)

    await this.page.waitForSelector("#dt_core_account-switcher_demo-tab")
    await this.page.click("#dt_core_account-switcher_demo-tab")
    await this.page.waitForTimeout(300)

    await this.page.waitForSelector(".dc-text.acc-switcher__balance")
    await this.page.click(".dc-text.acc-switcher__balance")
    await this.page.waitForTimeout(300)
  }

  async resetBalance() {
    await this.page.waitForSelector("#dt_core_account-info_acc-info")
    await this.page.click("#dt_core_account-info_acc-info")
    await this.page.waitForSelector(".dc-btn.dc-btn--secondary.dc-btn__small.acc-switcher__reset-account-btn")
    await this.page.click(".dc-btn.dc-btn--secondary.dc-btn__small.acc-switcher__reset-account-btn")
    await this.page.waitForTimeout(300)
  }

  async setup() {
    try {
      await this.page.waitForTimeout(2000)
      await this.page.goto("https://app.deriv.com/")

      await this.changeAccount()
      // セットアップ
      await this.page.waitForSelector(".ic-icon.ic-1HZ100V")
      await this.page.click(".ic-icon.ic-1HZ100V")
      await this.page.waitForTimeout(1000)
      await this.page.waitForSelector(".sc-mcd__item.sc-mcd__item--1HZ50V")
      await this.page.click(".sc-mcd__item.sc-mcd__item--1HZ50V")
      await this.page.waitForSelector("#dt_contract_dropdown")
      await this.page.waitForTimeout(300)
      await this.page.click("#dt_contract_dropdown")
      await this.page.waitForTimeout(300)
      await this.page.waitForSelector("#dt_contract_touch_item")
      await this.page.click("#dt_contract_touch_item")
      await this.page.waitForTimeout(300)
      await this.page.waitForSelector("#dc_m_toggle_item")
      await this.page.click("#dc_m_toggle_item")
      await this.page.waitForTimeout(300)
      await this.page.waitForSelector("#dt_simple_duration_input_sub")
      await this.page.click("#dt_simple_duration_input_sub")
      await this.page.waitForTimeout(300)
      await this.page.waitForSelector("#dt_barrier_1_input")
      await this.page.click("#dt_barrier_1_input")
      const inputValue = await this.page.$eval('#dt_barrier_1_input', el => el.value);
      for (let i = 0; i < inputValue.length; i++) {
        await this.page.keyboard.press('ArrowRight');
      }
      for (let i = 0; i < inputValue.length; i++) {
        await this.page.keyboard.press('Backspace');
      }
      await this.page.type("#dt_barrier_1_input", "+120")
    } catch (e) {
      console.log(e.message)
    }
  }

  async fix() {
    try {
      await this.page.waitForSelector(".ic-icon.ic-1HZ100V")
      await this.page.click(".ic-icon.ic-1HZ100V")
      await this.page.waitForTimeout(1000)
      await this.page.waitForSelector(".sc-mcd__item.sc-mcd__item--1HZ50V")
      await this.page.click(".sc-mcd__item.sc-mcd__item--1HZ50V")
      await this.page.waitForSelector("#dt_contract_dropdown")
      await this.page.waitForTimeout(300)
      await this.page.click("#dt_contract_dropdown")
      await this.page.waitForTimeout(300)
      await this.page.waitForSelector("#dt_contract_touch_item")
      await this.page.click("#dt_contract_touch_item")
      await this.page.waitForTimeout(300)
      await this.page.waitForSelector("#dc_m_toggle_item")
      await this.page.click("#dc_m_toggle_item")
      await this.page.waitForTimeout(300)
      await this.page.waitForSelector("#dt_simple_duration_input_sub")
      await this.page.click("#dt_simple_duration_input_sub")
      await this.page.waitForTimeout(300)
      await this.page.waitForSelector("#dt_barrier_1_input")
      await this.page.click("#dt_barrier_1_input")
      const inputValue = await this.page.$eval('#dt_barrier_1_input', el => el.value);
      for (let i = 0; i < inputValue.length; i++) {
        await this.page.keyboard.press('ArrowRight');
      }
      for (let i = 0; i < inputValue.length; i++) {
        await this.page.keyboard.press('Backspace');
      }
      await this.page.type("#dt_barrier_1_input", "+120")
    } catch (e) {
      console.log(e.message)
    }
  }


  async touch(param) {
    try {
      await this.page.waitForSelector("#dt_purchase_onetouch_button")
      await this.page.click("#dt_purchase_onetouch_button")
      let resultSelector = await this.page.$('.cq-animated-price.cq-current-price');
      let value = await (await resultSelector.getProperty('textContent')).jsonValue()
      console.log(value)
      return value
    } catch (e) {
      return e.message
    }
  }

  async noTouch(param) {
    try {
      await this.page.waitForSelector("#dt_purchase_notouch_button")
      await this.page.click("#dt_purchase_notouch_button")
      let resultSelector = await this.page.$('.cq-animated-price.cq-current-price');
      let value = await (await resultSelector.getProperty('textContent')).jsonValue()
      console.log(value)
      return value
    } catch (e) {
      return e.message
    }
  }

  async getCurrentPrice() {
    const resultSelector = await this.page.$('.cq-animated-price.cq-current-price');
    const value = await (await resultSelector.getProperty('textContent')).jsonValue()
    return value
  }

  async getCurrentBalance() {
    const resultSelector = await this.page.$('.acc-info__balance');
    const value = await (await resultSelector.getProperty('textContent')).jsonValue()
    return value
  }


  //スクリーンショットを撮る
  async screenshot(prefix) {
    const filename = `${prefix}_${format(new Date(), "yyyy-MM-dd_HH:mm:ss")}.jpeg`;
    const path = "/tmp/" + filename;
    try {
      await this.page.screenshot({ path: path });
      await slack.upload(path, filename);
    } catch(e) {
      console.error(e);
    }
  }

  //ログインしているかの確認
  async isLogedIn() {
    try {
      const frame = (await (await this.page.frames())[0].childFrames())[3]
      await (await frame.$$("a"))[2].click()
      const frame1 = (await (await this.page.frames())[0].childFrames())[0]
      await frame1.waitForSelector("img");
      const logoutElement = (await frame1.$$("img"))[8]
      return !!logoutElement
    } catch {
      return false
    }
  }
}

