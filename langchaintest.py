from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = OllamaLLM(model="llama3.2", temperature=0.1)

template = """  Summarize the following article in 1 concise sentence {article}   """

prompt = PromptTemplate.from_template(template)

parser = StrOutputParser()

chain = prompt | llm | parser

long_ahh_article =  """
I recently faced a bug when I was building a Web DApp with react.js and smart contract(solidity). The project was an NFT minting Dapp where customers can mint NFTs and own them.

I was sure everything was working very fine until I tested and noticed that the money customers were using to mint is not going to the owner’s wallet but going to the contract address.

That is so strange! What is the point of selling NFTs and you aren’t getting the money in your or where you can access it.

This is a very strange bug that we might not take note of until we see the effect. I learnt that CrytoPunk also faced the same issue which was why they launched version 2 of their NFTs.

So how do you solve this problem?

Money being stuck in the contract address can be removed if there is a withdrawal function that allows the owner to withdraw from the contract. See the code below.

Press enter or click to view image in full size

This function allows the owner to withdraw from the contract address by going to the scan address of the blockchain used like polygonscan for Polygon and etherscan for Ethereum.

Get Grace Olayinka Ajagbe’s stories in your inbox
Join Medium for free to get updates from this writer.

Enter your email
Subscribe
Noticing the only owner in the code means it is only the owner that can withdraw. If the withdrawal function is not restricted to only the owner, anybody will be able to withdraw.

Also note that to withdraw from the contract, you must have more than the amount you want to withdraw in your wallet.

But how do we make it so that when customers mint NFTs, it goes straight to the owner’s address while the transactions still show on the contract?

Inside your mint function in your contract, add the following line of code;

Press enter or click to view image in full size

owner() is a function in Ownable on the smart contract that stores the address that is used to deploy the contract as the owner’s address.

The full mint function looks like this;

Press enter or click to view image in full size

So when customers mint their NFTs to acquire them and they are being charged the amount to mint from Metamask, the last line of code in the mint function transfers the funds used to mint to the owner’s address i.e the owner of the contract.

These two functions have solved the issue of tokens getting stuck in the contract address and not being able to access or withdraw it.
"""

summary = chain.invoke({"article": long_ahh_article})

print(summary)