import hashlib, json, sys
import random
import copy
random.seed(0)


def hashMe(msg=""):
    if type(msg)!=str:
        msg = json.dumps(msg,sort_keys=True) 
        
    if sys.version_info.major == 2:
        return str(hashlib.sha256(msg).hexdigest(),'utf-8')
    else:
        return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()
    

def makeTransaction(maxValue=3):
    # This will create valid transactions in the range of (1,max)
    sign = int(random.getrandbits(1))*2 - 1   
    amount = random.randint(1,maxValue)
    user1Pay = sign * amount
    user2Pay = -1 * user1Pay
    return {u'User1':user1Pay,u'User2':user2Pay}

txnBuffer = [makeTransaction() for i in range(30)]
    
def updateState(txn, state):
    # checks if txn is valid then updates state
    state = state.copy() 
    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state

    
def isValidTxn(txn,state):
        #check sum of depo and withdraw
    if sum(txn.values()) is not 0:
        return False
    
    # check if it overdrafts
    for key in txn.keys():
        if key in state.keys(): 
            acctBalance = state[key]
        else:
            acctBalance = 0
        if (acctBalance + txn[key]) < 0:
            return False
    
    return True

#test
state = {u'User1': 5, u'User2': 5}
#-3 +3 for the user works normal returns true
print(isValidTxn({u'User1': -3, u'User2': 3}, state))
# returns false since you cant add or destroy coin
print(isValidTxn({u'User1': -4, u'User2': 3}, state))
#cant overdraft so returns false
print(isValidTxn({u'User1': -6, u'User2': 6},state))
#adding new users works
print(isValidTxn({u'User1': -4, u'User2': 2,'User3':2},state))

#each user starts with 50 coins
state = {u'User1':50, u'User2':50}  # Define the initial state
genesisBlockTxns = [state]
genesisBlockContents = {u'blockNumber':0,u'parentHash':None,u'txnCount':1,u'txns':genesisBlockTxns}
genesisHash = hashMe( genesisBlockContents )
genesisBlock = {u'hash':genesisHash,u'contents':genesisBlockContents}
genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)

chain = [genesisBlock]

def makeBlock(txns,chain):
    parentBlock = chain[-1]
    parentHash  = parentBlock[u'hash']
    blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
    txnCount    = len(txns)
    blockContents = {u'blockNumber':blockNumber,u'parentHash':parentHash,
                     u'txnCount':len(txns),'txns':txns}
    blockHash = hashMe( blockContents )
    block = {u'hash':blockHash,u'contents':blockContents}
    
    return block


blockSizeLimit = 5  # Arbitrary number of transactions per block- 
               #  this is chosen by the block miner, and can vary between blocks!

while len(txnBuffer) > 0:
    bufferStartSize = len(txnBuffer)
    
    ## Gather a set of valid transactions for inclusion
    txnList = []
    while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
        newTxn = txnBuffer.pop()
        validTxn = isValidTxn(newTxn,state) # This will return False if txn is invalid
        
        if validTxn:           # If we got a valid state, not 'False'
            txnList.append(newTxn)
            state = updateState(newTxn,state)
        else:
            print("ignored transaction")
            sys.stdout.flush()
            continue  # This was an invalid transaction; ignore it and move on
        
    ## Make a block
    myBlock = makeBlock(txnList,chain)
    chain.append(myBlock)  


print(chain[0])
print(chain[1])
print(state)

#check chain validiity

#checks to make sure block contents match the hash
def checkBlockHash(block):
    #raise exception if hash does not match
    expectedHash = hashMe (block['contents'])
    if block['hash'] != expectedHash:
        raise Exception('Hash does not match contents of block %s' %block['contents']['blockNumber'])
    return

#check validity of block given its current parent and system state
def checkBlockValidity(block,parent,state):
    #check each transaction are valid to state
    #block hash is valid for block contents
    #block number increment parent block by 1
    #accurately references block parent number

    parentNumber = parent['contents']['blockNumber']
    parentHash = parent['hash']
    blockNumber = block['contents']['blockNumber']

#check transation validity: throw error if invalid
    for txn in block['contents']['txns']:
        if isValidTxn(txn,state):
            state =updateState(txn,state)
        else:
            raise Exception("Invalid transaction in block %s"% ('blockNumber','txn'))
        
        checkBlockHash(block) #check hash

        if blockNumber !=(parentNumber+1):
            raise Exception("Hash does not match contents of the block %s"%blockNumber)
        
        if block['contents']['parentHash'] != parentHash:
            raise Exception ("Parent Hash not accurate at block number %s" %blockNumber)
        
    return state


#check validity of entire chain, and compute state starting from genesis block(first block). 
#will return if its valid, and raises error otherwise

def checkChain(chain):
    #check starting from genesis block
    #checking to make sure all transaction are valid (not overdraft, linked by hash)
    #returns state as dictionary of accounts and balances or return False if error

    #check chain is dictionary

    if type(chain) == str:
        try:
            chain = json.loads(chain)
            assert (type(chain)==list)
        except:
            return False
    elif type(chain)!= list:
        return False

    state = {}
    #check genesis block
    #check each transaction is valid
    #block hash is valid for block contents

    for txn in chain[0]['contents']['txns']:
        state = updateState(txn,state)
    checkBlockHash(chain[0])
    parent = chain[0]

    #check subsequent blocks
    #check each transaction is valid
    #block hash is valid for block contents

    for block in chain[1:]:
        state = checkBlockValidity(block,parent,state)
        parent = block

    return state

checkChain(chain)

chainAsText = json.dumps(chain,sort_keys=True)
checkChain(chainAsText)

#new node insertion
nodeBchain = copy.copy(chain)
nodeBtxns=[makeTransaction() for i in range(5)]
newBlock = makeBlock(nodeBtxns,nodeBchain)

print("Blockchain on Node A is currently %s blocks long "%len(chain))

try:
    print("New Block Recieved; checking validity...")
    state =checkBlockValidity(newBlock,chain[-1],state)
    chain.append(newBlock)
except:
    print("Invalid block; ignoring and waiting for next block...")

print("Blockchain on Node A is now %s blocks long"%len(chain))

    