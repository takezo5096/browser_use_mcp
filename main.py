import os
from csv import excel

from dotenv import load_dotenv
import requests
from urllib.parse import urlparse
from langchain_community.document_loaders import PyPDFLoader
from llm_selector import LLMSelector, LLMVendor
from mcp.server.fastmcp import FastMCP
from browser_use import Agent, Browser, BrowserConfig, Controller, ActionResult

load_dotenv()
#DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "downloads")
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

controller = Controller()

mcp = FastMCP("browser_use_mcp")

async def read_pdf(filename: str) -> list:
    file_path = f"{DOWNLOADS_DIR}/{filename}"
    if filename.startswith('/'):
        file_path = filename
    pages = []
    try:
        loader = PyPDFLoader(file_path)
        if loader is None:
            return []
        async for page in loader.alazy_load():
            pages.append(page)
    except Exception as e:
        return []

    return pages

@controller.action("PDFをダウンロードする")
async def download_pdf(url: str):
    url_data = requests.get(url).content
    a = urlparse(url)
    filename = os.path.basename(a.path)

    filename = DOWNLOADS_DIR + "/" + filename
    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(url_data)

    pdf_pages = await read_pdf(filename)
    if len(pdf_pages) == 0:
        return ActionResult(extracted_content=f"{filename}:このファイルはPDFではありません。違うものを探してください。")

    return ActionResult(extracted_content=f"{filename}という名前でPDFをダウンロードしました。")

@mcp.tool()
async def browser_use(task: str) -> str:
    """検索などブラウザが必要なタスクを処理する。
    Args
        task: タスクの内容を記載したテキスト
    """

    llm = LLMSelector.get_llm(LLMVendor.OPENAI, os.environ.get("OPENAI_MODEL_NAME"))
    if llm is None:
        raise Exception("can't load llm")

    browser_config = BrowserConfig(
        cdp_url=os.environ.get('CDP_URL', None),
        headless=False,
        disable_security=True,
        #chrome_instance_path='/usr/bin/google-chrome',
        extra_chromium_args=[
            "--enable-automation",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-window-activation",
            "--disable-focus-on-load",
            # "--headless" add headless if you need
        ]
    )

    browser = Browser(config=browser_config)

    #final_task = task + '\nダウンロードしたファイルがある場合はそのファイル名を出力してください。'
    final_task = task

    agent = None
    result = None
    try:
        agent = Agent(
            browser=browser,
            controller=controller,
            task=final_task,
            llm=llm,
            use_vision=False,
            generate_gif=False,
            max_actions_per_step=1,
            tool_calling_method="auto",
        )

        history = await agent.run(max_steps=20)
        result = history.final_result()
        if result is not None:
            result = result.replace("\n", "  \n") # markdownの改行は半角スペース２つ
    except Exception as e:
        await browser.close()
        return str(e)

    await browser.close()

    return result


if __name__ == "__main__":
    mcp.run(transport='stdio')
