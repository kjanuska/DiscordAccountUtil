const axios = require('axios').default;
const readline = require("readline");
const fs = require('fs');
const wait = require('util').promisify(setTimeout);

const userInput = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

async function join()
{
    let text = fs.readFileSync("./tokens.txt", "utf-8");
    const TOKENS = text.split("\n")
    userInput.question("Server invite code: ", function(code) {
        TOKENS.forEach(async (token) => {
            await axios.post(`https://discordapp.com/api/v9/invites/${code}`,
                {
                    headers: { 'authorization': token }
                });
            await wait(5000);
        })
        userInput.close();
    });}

join();