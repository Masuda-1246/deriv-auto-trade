require('dotenv').config();

const fs = require('fs');
const format = require("date-fns/format");

const { WebClient } = require('@slack/web-api');

const client = new WebClient(process.env["SLACK_TOKEN"]);
const channel = process.env["SLACK_CHANNEL"];

// function to tell if a data object is today
function isToday (someDate) {
    const today = new Date()
    return someDate.getDate() == today.getDate() &&
      someDate.getMonth() == today.getMonth() &&
      someDate.getFullYear() == today.getFullYear()
}

// function for sleep
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// function to tell if a file is downloaded
function awaitFileDownloaded (filePath) {
    let timeout = 5000
    const delay = 200

    return new Promise(async (resolve, reject) => {
        while (timeout > 0) {
            if (fs.existsSync(filePath)) {
                resolve(true);
                return
            } else {
                await sleep(delay)
                timeout -= delay
            }
        }
        reject("awaitFileDownloaded timed out")
    });
}



module.exports = {
    upload: async function(path, filename) {
        await client.files.upload({
            channels: channel, // log-core-sbi
            filename: filename,
            filetype: "jpeg",
            file: fs.createReadStream(path),
        })
    },

    notify: async function(msg, chan) {
        const targetThreadFile = `threads/thread_id_${chan}.txt` // e.g. thread_id_log-sbi-short.txt
        const isTargetThreadFile = fs.existsSync(targetThreadFile)
        var newThread = false;

        // check if necessary to make a new thread
        // true if no thread file or not today
        if (!isTargetThreadFile) {newThread = true}
        else {
            const slackTS = fs.readFileSync(targetThreadFile, 'utf8');
            const isTodaysThread = isToday(new Date(parseInt(slackTS * 1000))); // slackTS is second basis ---> millsecond basis
            if (!isTodaysThread) {newThread = true}
        };

        // post a new message and update ts in the file
        if (newThread) {
            const res = await client.chat.postMessage({
                channel: chan, // specify a channel
                text: `This is log on ${format(Date.now(), "yyyy-MM-dd")}`,
            });
            await fs.writeFileSync(targetThreadFile, res.message.ts);
            await awaitFileDownloaded(targetThreadFile) //wait until finish writing
        };

        // post msg on chan
        const targetSlackTS = await fs.readFileSync(targetThreadFile, 'utf8'); // read a new slackTS
        const isBroadcast = msg.includes("channel");
        await client.chat.postMessage({
                channel: chan, // specify a channel
                text: msg,
                thread_ts: targetSlackTS,
                reply_broadcast: isBroadcast
        });
    }
};
