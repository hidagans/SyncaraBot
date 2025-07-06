import importlib.util
import os
from syncara import console
import replicate

DYNAMIC_DIR = os.path.join(os.path.dirname(__file__), "dynamic")
PENDING_DIR = os.path.join(os.path.dirname(__file__), "pending")
os.makedirs(DYNAMIC_DIR, exist_ok=True)
os.makedirs(PENDING_DIR, exist_ok=True)

# Template AI untuk generate kode handler dari deskripsi
AI_HANDLER_TEMPLATE = '''
async def {func_name}(client, message, params):
    """{description}"""
    try:
        {body}
    except Exception as e:
        await message.reply(f'Error: {{e}}')
    return True
'''

def generate_handler_code(shortcode_name, description=None):
    func_name = shortcode_name.lower().replace(':', '_')
    sc_lower = shortcode_name.lower()
    desc = (description or '').lower()
    # Handler TAGALL
    if 'tagall' in sc_lower or 'tagall' in desc:
        body = (
            "members = []\n"
            "async for member in client.get_chat_members(message.chat.id):\n"
            "    if not member.user.is_bot:\n"
            "        members.append(f'@{member.user.username}' if member.user.username else member.user.first_name)\n"
            "mention_text = ' '.join(members)\n"
            "await message.reply(f'{params}\\n{mention_text}')"
        )
        return AI_HANDLER_TEMPLATE.format(func_name=func_name, description=description or 'Tag all group members', body=body)
    # Handler POLL
    if 'poll' in sc_lower or 'pool' in sc_lower or 'voting' in sc_lower or 'poll' in desc or 'voting' in desc:
        body = (
            "parts = params.split(':', 1)\n"
            "question = parts[0].strip() if parts else 'Poll'\n"
            "options = parts[1].split(',') if len(parts) > 1 else ['Ya', 'Tidak']\n"
            "await client.send_poll(message.chat.id, question, options)"
        )
        return AI_HANDLER_TEMPLATE.format(func_name=func_name, description=description or 'Create Telegram poll', body=body)
    # Handler REVERSE
    if 'reverse' in sc_lower or 'balik' in desc:
        body = "await message.reply(params[::-1])"
        return AI_HANDLER_TEMPLATE.format(func_name=func_name, description=description or 'Reverse string', body=body)
    # Handler LLM (Replicate Claude)
    try:
        prompt = f"""
Buatkan kode Python async function untuk handler Telegram bot.
Nama fungsi: {func_name}
Deskripsi: {description or '-'}
Fungsi harus menerima (client, message, params) dan membalas sesuai permintaan user.
Hanya tampilkan kode Python function-nya saja, tanpa penjelasan.
"""
        output = replicate.run(
            "anthropic/claude-4-sonnet",
            input={"prompt": prompt, "max_tokens": 512}
        )
        # Output Claude biasanya berupa string kode Python
        code = "".join(output) if isinstance(output, list) else str(output)
        # Validasi: harus mengandung 'async def'
        if 'async def' in code:
            return code
    except Exception as e:
        console.error(f"[DYNAMIC LLM] Error generate handler: {e}")
    # Fallback ke reverse string
    body = "await message.reply(params[::-1])"
    return AI_HANDLER_TEMPLATE.format(func_name=func_name, description=description or '', body=body)

# Handler baru masuk pending approval
async def request_handler_approval(shortcode_name, description, message):
    filename = os.path.join(PENDING_DIR, f"{shortcode_name.lower()}.py")
    code = generate_handler_code(shortcode_name, description)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    await message.reply(f"Handler `{shortcode_name}` siap di-approve.\n\nKode:\n```python\n{code}\n```\n\nBalas dengan /approve {shortcode_name} untuk mengaktifkan, atau /reject {shortcode_name} untuk membatalkan.")
    console.info(f"[DYNAMIC] Handler {shortcode_name} pending approval at {filename}")
    return filename

def approve_handler(shortcode_name, registry=None):
    pending_file = os.path.join(PENDING_DIR, f"{shortcode_name.lower()}.py")
    if not os.path.exists(pending_file):
        return False, "Handler tidak ditemukan di pending."
    dynamic_file = os.path.join(DYNAMIC_DIR, f"{shortcode_name.lower()}.py")
    os.rename(pending_file, dynamic_file)
    # Import handler
    spec = importlib.util.spec_from_file_location(shortcode_name, dynamic_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    handler_func = getattr(module, shortcode_name.lower().replace(':', '_'))
    if registry is not None:
        registry[shortcode_name] = handler_func
    console.info(f"[DYNAMIC] Handler {shortcode_name} approved and registered from {dynamic_file}")
    return True, "Handler sudah aktif!"

def reject_handler(shortcode_name):
    pending_file = os.path.join(PENDING_DIR, f"{shortcode_name.lower()}.py")
    if os.path.exists(pending_file):
        os.remove(pending_file)
        return True, "Handler dibatalkan."
    return False, "Handler tidak ditemukan di pending."

def create_and_register_handler(shortcode_name, description=None, registry=None):
    filename = os.path.join(DYNAMIC_DIR, f"{shortcode_name.lower()}.py")
    code = generate_handler_code(shortcode_name, description)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    # Import handler
    spec = importlib.util.spec_from_file_location(shortcode_name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    handler_func = getattr(module, shortcode_name.lower())
    if registry is not None:
        registry[shortcode_name] = handler_func
    console.info(f"[DYNAMIC] Handler {shortcode_name} registered from {filename}")
    return handler_func 