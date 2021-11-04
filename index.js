const axios = require('axios').default;
const readline = require("readline");
const fs = require('fs');

const userInput = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

async function join()
{
    let text = fs.readFileSync("./tokens.txt", "utf-8");
    const TOKENS = text.split("\n")
    userInput.question("Server invite code: ", function(code) {
        TOKENS.forEach(async (token, index) => {
            let waitTime = Math.floor(Math.random() * (60000 - 15000) + 15000)
            setTimeout(async () => {
                try {
                    await axios.post(`https://discordapp.com/api/v9/invites/${code}`,
                    {
                        headers: { 'authorization': token }
                    });
                } catch (error) {
                    console.log(error);
                }
            }, waitTime * index);
        })
        userInput.close();
    });
    console.log("All accounts joined!");
}

join();