"""Save WebIQ evidence incrementally; credentials remain in process env."""
import asyncio,json,os,sys
from pathlib import Path
import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
P=Path(__file__).resolve().parents[1]/'data/wenyu-western-raw.json'
async def main():
 jobs=json.loads(sys.argv[1]);data=json.loads(P.read_text()) if P.exists() else []
 async with httpx2.AsyncClient(headers={'x-apikey':os.environ['WEBIQ_API_KEY']},timeout=45) as client:
  async with streamable_http_client('https://api.microsoft.ai/v3/mcp',http_client=client) as (r,w):
   async with ClientSession(r,w) as s:
    await s.initialize()
    for job in jobs:
     args={'language':'zh','region':'CN','contentFormat':'text',**job['args']}
     result=await s.call_tool(job['tool'],args)
     d=result.structured_content
     if d is None:d=json.loads(next(c.text for c in result.content if hasattr(c,'text')))
     data.append({'tool':job['tool'],'arguments':args,'response':d})
     P.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
     results=d.get('webResults',[d])
     print(json.dumps({'query':args.get('query',args.get('url')),'results':[{'title':x.get('title'),'url':x.get('url'),'content':x.get('content','')[:2100]} for x in results]},ensure_ascii=False),flush=True)
asyncio.run(main())
