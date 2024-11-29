# encoding: utf-8
from dotenv import load_dotenv
import asyncio
import logging
import os
import hashlib
import time
from datetime import datetime
from kaspad.KaspadMultiClient import KaspadMultiClient
from deflationary_table import DEFLATIONARY_TABLE

# Load environment variables from the .env file
load_dotenv()

kaspad_hosts = []
for i in range(100):
    try:
        kaspad_hosts.append(os.environ[f"KASPAD_HOST_{i + 1}"].strip())
    except KeyError:
        break

if not kaspad_hosts:
    raise Exception('Please set at least KASPAD_HOST_1 environment variable.')

kaspad_client = KaspadMultiClient(kaspad_hosts)

async def get_coinsupply():
    """
    Get $KAS coin supply information
    """
    resp = await kaspad_client.request("getCoinSupplyRequest")
    return {
        "circulatingSupply": resp["getCoinSupplyResponse"].get("circulatingSompi", 0),
        "totalSupply": resp["getCoinSupplyResponse"].get("circulatingSompi", 0),
        "maxSupply": resp["getCoinSupplyResponse"]["maxSompi"]
    }

async def get_halving(field):
    """
    Returns information about chromatic halving
    """
    resp = await kaspad_client.request("getBlockDagInfoRequest")
    daa_score = int(resp["getBlockDagInfoResponse"]["virtualDaaScore"])

    future_reward = 0
    daa_breakpoint = 0

    daa_list = sorted(DEFLATIONARY_TABLE)

    for i, to_break_score in enumerate(daa_list):
        if daa_score < to_break_score:
            future_reward = DEFLATIONARY_TABLE[daa_list[i + 1]]
            daa_breakpoint = to_break_score
            break

    next_halving_timestamp = int(time.time() + (daa_breakpoint - daa_score))

    if field == "nextHalvingTimestamp":
        return PlainTextResponse(content=str(next_halving_timestamp))

    elif field == "nextHalvingDate":
        return PlainTextResponse(content=datetime.utcfromtimestamp(next_halving_timestamp)
                                 .strftime('%Y-%m-%d %H:%M:%S UTC'))

    elif field == "nextHalvingAmount":
        return PlainTextResponse(content=str(future_reward))

    else:
        return {
            "nextHalvingTimestamp": next_halving_timestamp,
            "nextHalvingDate": datetime.utcfromtimestamp(next_halving_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC'),
            "nextHalvingAmount": future_reward
        }

async def get_blockdag():
    """
    Get some global Kaspa BlockDAG information
    """
    resp = await kaspad_client.request("getBlockDagInfoRequest")
    return resp["getBlockDagInfoResponse"]

async def get_kaspad_info():
    """
    Get some information for kaspad instance, which is currently connected.
    """
    resp = await kaspad_client.request("getInfoRequest")
    p2p_id = resp["getInfoResponse"].pop("p2pId")
    resp["getInfoResponse"]["p2pIdHashed"] = hashlib.sha256(p2p_id.encode()).hexdigest()
    return resp["getInfoResponse"]


async def main():
  await kaspad_client.initialize_all()

  print("")
  print("COIN SUPPLY:")
  print(await get_coinsupply())

  print("")
  print("BLOCKDAG:")
  print(await get_blockdag())

  print("")
  print("KASPA INFO:")
  print(await get_kaspad_info())

  print("")
  print("KASPA INFO:")
  print(await get_kaspad_info())

  print("")
  print("HALVING:")
  print(await get_halving(""))

asyncio.run(main())  # main loop