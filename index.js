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
        code = code.replace('https://discord.gg/', '');
        TOKENS.forEach(async (token, index) => {
            let waitTime = Math.floor(Math.random() * (60000 - 15000) + 15000)
            setTimeout(async () => {
                try {
                    await axios.post(`https://discordapp.com/api/v9/invites/${code}`,
                    {
                        headers: {
                            'authorization': token,
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
                        }
                    });
                } catch (error) {
                    console.log(error);
                }
            }, waitTime * index);
        })
        userInput.close();
    });
    // await console.log("All accounts joined!");
}