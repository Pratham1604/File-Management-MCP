from mcp.server.fastmcp import FastMCP
import aiofiles
import shutil
import os
import asyncio
import argparse

mcp = FastMCP()

loop = asyncio.get_event_loop()

def simple_response(action: str, path: str, extra: str = ""):
    return f"{action} at {path} → {extra}" if extra else f"{action} at {path}"


@mcp.tool("/upload/{path}/{file_name}")
async def upload_file(path: str, file_name: str, file_content: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
        full_path = os.path.join(path, file_name)
        async with aiofiles.open(full_path, "w") as f:
            await f.write(file_content)
        return f"File '{file_name}' uploaded at {path}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/delete_file/{path}")
def delete_file(path: str) -> str:
    try:
        os.remove(path)
        return simple_response("File deleted", path)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/create_folder/{path}")
def create_folder(path: str) -> str: 
    try:
        os.makedirs(path, exist_ok=True)
        return simple_response("Folder created", path)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/delete_folder/{path}")
def delete_folder(path: str) -> str:
    try:
        os.rmdir(path)
        return simple_response("Folder deleted", path)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/rename_file/{path}/{new_name}")
def rename_file(path: str, new_name: str) -> str:
    try:
        base = os.path.dirname(path)
        new_path = os.path.join(base, new_name)
        os.rename(path, new_path)
        return simple_response("File renamed", path, f"→ {new_path}")
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/rename_folder/{path}/{new_name}")
def rename_folder(path: str, new_name: str) -> str:
    return rename_file(path, new_name)

@mcp.tool("/move_file/{path}/{new_path}")
def move_file(path: str, new_path: str) -> str:
    try:
        shutil.move(path, new_path)
        return simple_response("File moved", path, f"→ {new_path}")
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/move_folder/{path}/{new_path}")
def move_folder(path: str, new_path: str) -> str:
    return move_file(path, new_path)

@mcp.tool("/copy_file/{path}/{new_path}")
def copy_file(path: str, new_path: str) -> str:
    try:
        shutil.copy2(path, new_path)
        return simple_response("File copied", path, f"→ {new_path}")
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/copy_folder/{path}/{new_path}")
def copy_folder(path: str, new_path: str) -> str:
    try:
        shutil.copytree(path, new_path)
        return simple_response("Folder copied", path, f"→ {new_path}")
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/list_path/{path}")
async def list_path_content(path: str) -> list:
    try:
        if await asyncio.to_thread(os.path.isdir, path):
            return await asyncio.to_thread(os.listdir, path)
        elif await asyncio.to_thread(os.path.isfile, path):
            return [os.path.basename(path)]
        else:
            return [f"Error: Path does not exist or is not accessible → {path}"]
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool("/file_content/{path}")
async def get_file_content(path: str) -> str:
    try:
        async with aiofiles.open(path, mode='r') as f:
            return await f.read()
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/folder_content/{path}")
async def get_folder_content(path: str) -> str:
    try:
        return ", ".join(await asyncio.to_thread(os.listdir, path)) if os.path.isdir(path) else "Invalid folder"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/file_size/{path}")
async def get_file_size(path: str) -> str:
    try:
        size = await asyncio.to_thread(os.path.getsize, path)
        return f"{size} bytes"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/folder_size/{path}")
async def get_folder_size(path: str) -> str:
    try:
        def calc():
            total = 0
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.isfile(fp):
                        total += os.path.getsize(fp)
            return total
        total = await asyncio.to_thread(calc)
        return f"{total} bytes"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/file_type/{path}")
async def get_file_type(path: str) -> str:
    try:
        return "Directory" if os.path.isdir(path) else "File"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool("/file_metadata/{path}")
async def get_file_metadata(path: str) -> str:
    try:
        stat = await asyncio.to_thread(os.stat, path)
        return f"Size: {stat.st_size}, Created: {stat.st_ctime}, Modified: {stat.st_mtime}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    print("🚀Starting server... ")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="stdio", choices=["sse", "stdio"]
    )
    print("Server type: ", parser.parse_args().server_type)
    print("Launching on Port: ", 3000)
    print('Check "http://localhost:3000/sse" for the server status')

    args = parser.parse_args()
    mcp.run(args.server_type)

    # Debug Mode
    #  uv run mcp dev server.py

    # Production Mode
    # uv run server.py --server_type=sse